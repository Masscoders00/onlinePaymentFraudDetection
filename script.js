document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('fraud-detection-form');
    const resultSection = document.getElementById('result');
    const resultContent = document.getElementById('result-content');

    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading state
            resultSection.classList.remove('hidden');
            resultContent.innerHTML = '<div class="loading">Processing transaction...</div>';
            
            // Get form data
            const formData = new FormData(form);
            
            // Send request to server
            fetch('/predict', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Display result
                displayResult(data);
            })
            .catch(error => {
                resultContent.innerHTML = `
                    <div class="error-message">
                        <p>Error: ${error.message || 'Something went wrong. Please try again.'}</p>
                    </div>
                `;
            });
        });
    }

    function displayResult(data) {
        if (data.error) {
            resultContent.innerHTML = `
                <div class="error-message">
                    <p>Error: ${data.error}</p>
                </div>
            `;
            return;
        }

        // Determine result class based on risk level
        let resultClass = '';
        if (data.risk_level === 'Low') {
            resultClass = 'result-low';
        } else if (data.risk_level === 'Medium') {
            resultClass = 'result-medium';
        } else {
            resultClass = 'result-high';
        }

        // Format probability as percentage
        const fraudProbability = (data.fraud_probability * 100).toFixed(2);

        // Create result HTML
        const resultHTML = `
            <div class="result-card ${resultClass}">
                <h4>Risk Level: ${data.risk_level}</h4>
                <p>${data.is_fraud ? 'This transaction is likely fraudulent!' : 'This transaction appears legitimate.'}</p>
                <p>Fraud Probability: ${fraudProbability}%</p>
            </div>
            
            <div class="result-details">
                <h4>Transaction Analysis</h4>
                <ul>
                    <li>
                        <span>Fraud Probability:</span>
                        <span>${fraudProbability}%</span>
                    </li>
                    <li>
                        <span>Risk Assessment:</span>
                        <span>${data.risk_level}</span>
                    </li>
                    <li>
                        <span>Model Used:</span>
                        <span>${data.model_used}</span>
                    </li>
                </ul>
                
                <div class="recommendation">
                    <h4>Recommendation</h4>
                    <p>${getRecommendation(data.risk_level, data.fraud_probability)}</p>
                </div>
            </div>
        `;

        resultContent.innerHTML = resultHTML;
        
        // Scroll to result
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    function getRecommendation(riskLevel, probability) {
        if (riskLevel === 'Low') {
            return 'This transaction can be processed normally.';
        } else if (riskLevel === 'Medium') {
            return 'Consider additional verification steps before processing this transaction.';
        } else {
            return 'This transaction should be blocked and investigated for potential fraud.';
        }
    }
});