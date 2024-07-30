const register_form = document.querySelector(".register-form")
const warning = document.getElementById("passwordHelp")
const password = document.getElementById("password")
const confirmPassword = document.getElementById("confirmPassword")
const passwordCheckbox = document.getElementById("passwordCheckbox")
const send_btn = document.querySelector(".send-btn")
var symbols = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/
passwordCheckbox.addEventListener("change", (e)=>{
    if(e.currentTarget.checked){
        password.type = "text"
        confirmPassword.type = "text"
    }else{
        password.type = "password"
        confirmPassword.type = "password"
    }
})
function passwordOk(str){
    if(/[A-Z]/.test(str) && /[0-9]/.test(str) && symbols.test(str)){
        return true
    }else{
        return false
    }
}
function handleSubmit(e){
    e.preventDefault()
    if(!passwordOk(e.currentTarget.password.value)){
        warning.innerHTML = "La contraseña debe contener mayusculas, numeros y simbolos"
    }else{
        if(e.currentTarget.password.value.length<8){
            warning.innerHTML="La contraseña deben tener al menos 8 caracteres"
        }else{
            if(e.currentTarget.password.value === e.currentTarget.confirmPassword.value){
                warning.innerHTML = ""
                e.currentTarget.submit()
            }else{
                warning.innerHTML = "Las contraseñas deben coincidir"
            }
        }
    }
}
register_form.addEventListener("submit", (e)=>{
    handleSubmit(e)
})