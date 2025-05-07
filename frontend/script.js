fetch('http://localhost:8000/')
  .then(response => response.json())
  .then(data => console.log(data));

  
  
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.login').addEventListener('click', () => {
        console.log('Log in button clicked');
    });

    document.querySelector('.register').addEventListener('click', () => {
        console.log('Register button clicked');
    });
});


// V2_Log-in_page

let emailId = document.getElementById("email-id");
let errorMsg = document.getElementById("error-msg");
let icon = document.getElementById("icon");
let mailRegex = /^[a-zA-Z][a-zA-Z0-9\-\_\.]+@[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}$/;

function checker(){
    icon.style.display="none";
    if(emailId.value.match(mailRegex)){
        icon.innerHTML = '<i class="fas fa-check-circle"></i>';
        icon.style.color = '#2ecc71';
        errorMsg.style.display = 'none';
        emailId.style.border = '2px solid #2ecc71';
    }
    else if(emailId.value == ""){
        icon.style.display = 'none';
        errorMsg.style.display = 'none';
        emailId.style.border = '2px solid #d1d3d4';
    }
    else{
        icon.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
        icon.style.color = '#ff2851';
        errorMsg.style.display = 'block';
        emailId.style.border = '2px solid #ff2851';
    }

}


const passwordInput = document.getElementById('password-id');
const toggleCheckbox = document.getElementById('togglePassword');

toggleCheckbox.addEventListener('change', function () {
  if (this.checked) {
    passwordInput.type = 'text';
  } else {
    passwordInput.type = 'password';
  }
});

