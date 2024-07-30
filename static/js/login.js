const password = document.getElementById("password")
const passwordCheckbox = document.getElementById("passwordCheckbox")
passwordCheckbox.addEventListener("change", (e)=>{
    if(e.currentTarget.checked){
        password.type = "text"
    }else{
        password.type = "password"
    }
})