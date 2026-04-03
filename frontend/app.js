document.addEventListener('DOMContentLoaded', () => {
    const evaluateBtn = document.getElementById('evaluateBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const resultsSection = document.getElementById('resultsSection');
    
    // API endpoint configured for standard local FastAPI running
    const API_URL = "http://localhost:8000/evaluate";

    evaluateBtn.addEventListener('click', async () => {
        const question = document.getElementById('question').value.trim();
        const studentAnswer = document.getElementById('studentAnswer').value.trim();
        const totalMarks = parseFloat(document.getElementById('totalMarks').value);

        if (!question || !studentAnswer) {
            alert('Please provide both the Question and the Student Answer.');
            return;
        }
        if (isNaN(totalMarks) || totalMarks <= 0) {
            alert('Please set a valid positive maximum score.');
            return;
        }

        // Set Loading state
        toggleLoadingState(true);
        resultsSection.classList.add('hidden'); // Hide old results

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    student_answer: studentAnswer,
                    total_marks: totalMarks
                })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            renderResults(data);
        } catch (error) {
            console.error('Evaluation failed:', error);
            alert('Evaluation failed. Make sure the backend server (FastAPI) is running at ' + API_URL + '\n\nError details: ' + error.message);
        } finally {
            // Unset loading state
            toggleLoadingState(false);
        }
    });

    function toggleLoadingState(isLoading) {
        if (isLoading) {
            evaluateBtn.disabled = true;
            btnText.classList.add('hidden');
            btnSpinner.classList.remove('hidden');
        } else {
            evaluateBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnSpinner.classList.add('hidden');
        }
    }

    function renderResults(data) {
        // Render Final Score
        document.getElementById('awardedMarks').textContent = data.total_marks_awarded;
        document.getElementById('maxMarksFinal').textContent = data.maximum_marks;
        document.getElementById('studentFeedback').textContent = data.feedback_for_student;

        // Render Errors if any
        const errorCard = document.getElementById('errorCard');
        const errorList = document.getElementById('errorList');
        errorList.innerHTML = ''; // clear

        const allErrors = [
            ...data.error_analysis.conceptual_errors.map(e => `[Concept] ${e}`),
            ...data.error_analysis.procedural_errors.map(e => `[Procedural] ${e}`),
            ...data.error_analysis.calculation_errors.map(e => `[Calculation] ${e}`),
            ...data.error_analysis.presentation_errors.map(e => `[Presentation] ${e}`)
        ];

        if (allErrors.length > 0) {
            allErrors.forEach(err => {
                const li = document.createElement('li');
                li.textContent = err;
                errorList.appendChild(li);
            });
            errorCard.classList.remove('hidden');
        } else {
            errorCard.classList.add('hidden');
        }

        // Render Step Breakdown
        const stepsContainer = document.getElementById('stepsContainer');
        stepsContainer.innerHTML = '';

        data.step_by_step_breakdown.forEach((step) => {
            const stepDiv = document.createElement('div');
            stepDiv.className = 'step-item';

            const infoDiv = document.createElement('div');
            infoDiv.className = 'step-info';
            infoDiv.innerHTML = `
                <p>${step.step_description}</p>
                <div class="step-status status-${step.status}">${step.status}</div>
            `;

            const marksDiv = document.createElement('div');
            marksDiv.className = 'step-marks';
            marksDiv.textContent = `${step.marks_awarded}/${step.max_marks_for_step}`;

            stepDiv.appendChild(infoDiv);
            stepDiv.appendChild(marksDiv);
            stepsContainer.appendChild(stepDiv);
        });

        // Show Results
        resultsSection.classList.remove('hidden');
    }
});
