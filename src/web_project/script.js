document.getElementById('submitBtn').addEventListener('click', function() {
    var progressBarContainer = document.getElementById('progressBarContainer');
    var progressBar = document.getElementById('progressBar');
    progressBarContainer.classList.remove('hidden');
    progressBar.style.width = '0%';

    var width = 0;
    var intervalTime = document.getElementById('includeImages').checked ? 2 : 1;
    var interval = setInterval(function() {
        width += intervalTime;
        progressBar.style.width = width + '%';
        if (width >= 100) {
            clearInterval(interval);
            window.location.href = 'view_img_pag2.html';
        }
    }, 300);

    var texto = document.getElementById('inputText').value;
    var incluir_img = document.getElementById('includeImages').checked;

    var data = {
        'texto': texto,
        'incluir_img': incluir_img
    };

    fetch('http://localhost:5000/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(response => response.json())
      .then(data => console.log(data))
      .catch((error) => {
        console.error('Error:', error);
    });
});
