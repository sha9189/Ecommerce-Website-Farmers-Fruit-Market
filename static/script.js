// Make the right navigation button active

let link = window.location.href
let start = link.lastIndexOf("/")
let page = link.slice(start)

if (page == "/"){
    document.getElementById("buy_btn").classList.add("active")
}
else if (page == "/cart"){
    document.getElementById("cart_btn").classList.add("active")
}
else if (page == "/login"){
    document.getElementById("login_btn").classList.add("active")
}
else if (page == "/register"){
    document.getElementById("register_btn").classList.add("active")
}