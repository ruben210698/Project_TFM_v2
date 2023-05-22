const images = [  'imagen0.png', 'imagen1.png',  'imagen2.png',  'imagen3.png',  'imagen4.png', 'imagen5.png', 'imagen6.png', 'imagen7.png', 'imagen8.png',
                  'imagen9.png', 'imagen10.png', 'imagen11.png', 'imagen12.png', 'imagen13.png', 'imagen14.png'];

let counter = 0;
let max_counter = 0
let new_image = 1
let texto_recibido = 0

function checkImageExistence(imageUrl) {
  return fetch(imageUrl)
    .then(response => {
      if (!response.ok) {
        throw new Error('La imagen no existe');
      }
    });
}
function showImage(index, suma) {
  console.log('max_counter:', max_counter);
  const container = document.getElementById('image-container');
  const imageName = `imagen${counter}.png`;
  const imageUrl = `imagenes/${imageName}`;

  checkImageExistence(imageUrl)
    .then(() => {
      const imgElement = document.createElement('img');
      imgElement.src = imageUrl;
      container.innerHTML = '';
      container.appendChild(imgElement);
      console.log('Nombre de la imagen:', imageName);
      // max_counter = counter if maxmax_counter < counter else max_counter
      if (max_counter < counter) {
        max_counter = counter;
      }
    })
    .catch(error => {
      const imageName = `imagen${max_counter}.png`;
      const imageUrl = `imagenes/${imageName}`;
      const imgElement = document.createElement('img');
      imgElement.src = imageUrl;
      container.innerHTML = '';
      container.appendChild(imgElement);
      counter = counter - suma;
    });


  //console.log('Nombre de la imagen:', imageName);
  //container.style.backgroundImage = `url(imagenes/${imageName})`;
  ////container.style.backgroundImage = `url(imagenes/imagen1.png)`;
}

function previousImage() {
  new_image = 0
  if (counter > 0) {
    counter--;
    console.log('Nuevo valor del contador:', counter);
    showImage(counter, -1);
  } else {
    console.log('Nuevo valor del contador:', counter);
    showImage(counter, 0);
  }
}

function nextImage() {
    new_image = 0
  if (counter < 100) {
    counter++;
    console.log('Nuevo valor del contador:', counter);
    showImage(counter, 1);
  }
}

document.getElementById('previous').addEventListener('click', previousImage);
document.getElementById('next').addEventListener('click', nextImage);

document.addEventListener('DOMContentLoaded', function() {
  var enviarBtn = document.getElementById('enviar-btn');
  enviarBtn.addEventListener('click', enviarTexto);
});


function enviarTexto() {
  new_image = 1
  texto_recibido = 0
  var textoInput = document.getElementById('texto-input').value;

  // Realizar una petición al proceso Python
  var url = 'http://localhost:5000/';
  var data = {
    texto: textoInput
  };

  fetch(url, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(function(response) {
    return response.json();
  })
  .then(function(data) {
    // Aquí puedes manejar la respuesta de tu proceso Python
    // por ejemplo, mostrar la imagen generada en el contenedor 'image-container'
    var imageContainer = document.getElementById('image-container');
    var img = document.createElement('img');
    img.src = data.ruta_imagen; // suponiendo que la respuesta de Python incluye la ruta de la imagen
    imageContainer.innerHTML = ''; // Limpiar el contenedor
    imageContainer.appendChild(img);


  })
  .catch(function(error) {
    console.error('Error:', error);
  });
}

// fetch('http://localhost:5000/borrar-imagenes', {
//   method: 'POST'
// })
// .then(function(response) {
//   if (response.ok) {
//     console.log('Imágenes borradas exitosamente');
//   } else {
//     console.error('Error al borrar las imágenes');
//   }
// })
// .catch(function(error) {
//   console.error('Error:', error);
// });


// showImage();













function showImagePeriodic() {
  if (new_image) {
    showImage(counter, 0)
  }
}



// Verificar cambios en la carpeta cada segundo
setInterval(showImagePeriodic, 3000);
setInterval(obtenerTexto, 1000);





function obtenerTexto() {
    if (texto_recibido) {
        return
    }
  fetch('http://localhost:5000/obtener_prints_python', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => response.json())
    .then(data => {
      console.log('Texto desde Python:', data.texto);
      document.getElementById('texto-container').textContent = data.texto;
        if (data.texto.length > 100) {
          texto_recibido = 1
        }
    })
    .catch(error => {
      console.error('Error:', error);
    });
}