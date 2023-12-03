function showOutput() {
    event.preventDefault();
    let outputElement = document.getElementById('output');
    outputElement.style.display = 'block';
}

function loadOutput() {
    event.preventDefault();
    // Use the Fetch API to load text from another file
    fetch('output.txt')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(text => {
            // Update the output container with the loaded text
            let outputContainer = document.getElementById('outputContainer');
            let outputElement = document.getElementById('output');
            outputElement.innerText = text;
            outputContainer.style.display = 'block';
            document.getElementById('explainButton').removeAttribute('disabled');
            document.getElementById('ratingSection').style.display = 'block';
        })
        .catch(error => console.error('Error fetching data:', error));
}

function loadExplanation() {
    event.preventDefault();
    // Use the Fetch API to load text from another file
    fetch('explanation.txt')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(text => {
            // Update the output container with the loaded text
            let explainContainer = document.getElementById('explanationContainer');
            let explainElement = document.getElementById('explanation');
            explainElement.innerText = text;
            explainContainer.style.display = 'block';
        })
        .catch(error => console.error('Error fetching data:', error));
}

function setAPIInputText(value) {
    let apiInput = document.getElementById('apiInput');
    apiInput.value = value;
}

function showFunctions(apiName) {
    const apiFunctions = {
        'pandas': ['dataframe.size()', 'dataframe.empty()'],
        'Hugging Face' : ['tokenizer.convert_ids_to_tokens()'],
        'numpy': ['numpy.sum()', 'numpy.mean()']
    };

    const functionContainer = document.getElementById('functionContainer');

    // Clear previous content
    functionContainer.innerHTML = '';

    const functions = apiFunctions[apiName] || [];

    // Create buttons for each function
    functions.forEach(func => {
        const button = document.createElement('button');
        button.textContent = func;
        button.addEventListener('click', () => {
            document.getElementById('selectedFunction').value = func;
        });

        // Apply the same styling as API buttons
        button.style.margin = '3px';
        button.style.cursor = 'pointer';

        functionContainer.appendChild(button);
    });

    // Make the function container visible
    functionContainer.style.display = 'block';
}

function clearFunctions() {
    document.getElementById('functionContainer').innerHTML = '';
    document.getElementById('selectedFunction').value = '';
}

function showNegativeFeedback() {
    // Show the hidden buttons
    document.getElementById('tooLong').style.display = 'inline-block';
    document.getElementById('tooShort').style.display = 'inline-block';
}