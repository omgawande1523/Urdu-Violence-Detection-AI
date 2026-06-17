import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, 
    roc_auc_score, precision_recall_curve, auc, confusion_matrix
)
from scipy import stats

def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None, num_classes: int = 2) -> Dict[str, Any]:
    """Calculates all metrics requested including F1, Precision, Recall, ROC-AUC, PR-AUC."""
    accuracy = accuracy_score(y_true, y_pred)
    
    # Precision, Recall, F1
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary' if num_classes == 2 else 'macro', zero_division=0)
    
    # Specific class-wise details
    class_precision, class_recall, class_f1, _ = precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0)
    
    metrics = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "class_metrics": {
            i: {
                "precision": float(class_precision[i]),
                "recall": float(class_recall[i]),
                "f1": float(class_f1[i])
            } for i in range(len(class_precision))
        }
    }
    
    # Calculate ROC-AUC and PR-AUC if probabilities are available
    if y_prob is not None:
        try:
            if num_classes == 2:
                # Binary ROC AUC (y_prob should be the probability of class 1)
                metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
                
                # PR AUC
                prec_curve, rec_curve, _ = precision_recall_curve(y_true, y_prob)
                metrics["pr_auc"] = float(auc(rec_curve, prec_curve))
            else:
                # Multiclass ROC AUC (OVR)
                metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob, multi_class='ovr'))
                metrics["pr_auc"] = 0.0 # Standard multiclass PR AUC is complex, default to 0
        except Exception as e:
            metrics["roc_auc"] = None
            metrics["pr_auc"] = None
            
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    metrics["confusion_matrix"] = cm.tolist()
    
    return metrics

def compare_models_significance(model_a_preds: np.ndarray, model_b_preds: np.ndarray, y_true: np.ndarray) -> Dict[str, Any]:
    """Performs statistical significance testing (McNemar's test or Wilcoxon signed-rank test)."""
    # 0 for incorrect prediction, 1 for correct prediction
    correct_a = (model_a_preds == y_true).astype(int)
    correct_b = (model_b_preds == y_true).astype(int)
    
    # Contingency table for McNemar's test
    # a_correct & b_correct, a_correct & b_incorrect
    # a_incorrect & b_correct, a_incorrect & b_incorrect
    n00 = np.sum((correct_a == 0) & (correct_b == 0))
    n01 = np.sum((correct_a == 0) & (correct_b == 1))
    n10 = np.sum((correct_a == 1) & (correct_b == 0))
    n11 = np.sum((correct_a == 1) & (correct_b == 1))
    
    # McNemar's test statistic
    if (n01 + n10) > 0:
        stat = ((abs(n01 - n10) - 0.5) ** 2) / (n01 + n10) # Yates continuity correction
        p_value = 1.0 - stats.chi2.cdf(stat, 1)
    else:
        stat = 0.0
        p_value = 1.0
        
    return {
        "mcnemar_stat": float(stat),
        "p_value": float(p_value),
        "are_significantly_different": bool(p_value < 0.05),
        "contingency_table": [[int(n11), int(n10)], [int(n01), int(n00)]]
    }

def perform_error_analysis(df: pd.DataFrame, y_true: np.ndarray, y_pred: np.ndarray) -> List[Dict[str, Any]]:
    """Identifies and extracts misclassified examples for manual analyst review."""
    errors = []
    for idx, (true, pred) in enumerate(zip(y_true, y_pred)):
        if true != pred:
            errors.append({
                "index": int(idx),
                "text": df.iloc[idx]["text"] if "text" in df.columns else "",
                "true_label": int(true),
                "predicted_label": int(pred)
            })
    return errors

def generate_evaluation_report(metrics: Dict[str, Any], val_errors: List[Dict[str, Any]], title: str = "Model Performance Evaluation Report") -> str:
    """Generates an HTML evaluation report formatted for the frontend viewer."""
    cm = metrics.get("confusion_matrix", [])
    cm_html = ""
    if cm:
        cm_html = f"""
        <table class="min-w-full text-center border-collapse">
            <thead>
                <tr>
                    <th class="border p-2">Actual / Predicted</th>
                    <th class="border p-2">Predicted Neg</th>
                    <th class="border p-2">Predicted Pos</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="border p-2 font-bold">Actual Neg</td>
                    <td class="border p-2 bg-green-100 text-green-800">{cm[0][0]}</td>
                    <td class="border p-2 bg-red-100 text-red-800">{cm[0][1]}</td>
                </tr>
                <tr>
                    <td class="border p-2 font-bold">Actual Pos</td>
                    <td class="border p-2 bg-red-100 text-red-800">{cm[1][0]}</td>
                    <td class="border p-2 bg-green-100 text-green-800">{cm[1][1]}</td>
                </tr>
            </tbody>
        </table>
        """

    errors_html = ""
    for error in val_errors[:10]: # Cap at 10 for readability
        errors_html += f"""
        <div class="border-b py-2 text-sm">
            <p class="font-medium text-red-600">Predicted: {error['predicted_label']} | Actual: {error['true_label']}</p>
            <p class="text-gray-700 italic">"{error['text']}"</p>
        </div>
        """

    html = f"""
    <div class="p-6 bg-white rounded-lg shadow">
        <h1 class="text-2xl font-bold text-gray-900 mb-4">{title}</h1>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="p-4 bg-blue-50 rounded">
                <p class="text-xs text-blue-600 font-semibold uppercase">Accuracy</p>
                <p class="text-xl font-bold text-blue-900">{metrics.get('accuracy', 0.0):.4f}</p>
            </div>
            <div class="p-4 bg-green-50 rounded">
                <p class="text-xs text-green-600 font-semibold uppercase">Precision</p>
                <p class="text-xl font-bold text-green-900">{metrics.get('precision', 0.0):.4f}</p>
            </div>
            <div class="p-4 bg-indigo-50 rounded">
                <p class="text-xs text-indigo-600 font-semibold uppercase">Recall</p>
                <p class="text-xl font-bold text-indigo-900">{metrics.get('recall', 0.0):.4f}</p>
            </div>
            <div class="p-4 bg-purple-50 rounded">
                <p class="text-xs text-purple-600 font-semibold uppercase">F1-Score</p>
                <p class="text-xl font-bold text-purple-900">{metrics.get('f1', 0.0):.4f}</p>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Confusion Matrix</h3>
                {cm_html}
            </div>
            <div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Additional Metrics</h3>
                <ul class="text-sm text-gray-600 space-y-1">
                    <li><strong>ROC AUC:</strong> {f"{metrics.get('roc_auc', 0.0):.4f}" if metrics.get('roc_auc') else 'N/A'}</li>
                    <li><strong>PR AUC:</strong> {f"{metrics.get('pr_auc', 0.0):.4f}" if metrics.get('pr_auc') else 'N/A'}</li>
                </ul>
            </div>
        </div>

        <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Sample Error Analysis</h3>
            <div class="space-y-2 max-h-60 overflow-y-auto border p-3 rounded">
                {errors_html if errors_html else '<p class="text-sm text-gray-500">No misclassification errors found.</p>'}
            </div>
        </div>
    </div>
    """
    return html
