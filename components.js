document.addEventListener("DOMContentLoaded", function() {
    // Load Navbar
    fetch("navbar.html")
        .then(response => response.text())
        .then(data => {
            document.getElementById("navbar-placeholder").innerHTML = data;
            highlightActiveLink();
        });

    // Load Footer
    fetch("footer.html")
        .then(response => response.text())
        .then(data => {
            document.getElementById("footer-placeholder").innerHTML = data;
        });
});

function highlightActiveLink() {
    const currentPath = window.location.pathname.split("/").pop() || "index.html";
    const navLinks = document.querySelectorAll(".nav-links a");
    
    navLinks.forEach(link => {
        // Get the href attribute
        const href = link.getAttribute("href");
        
        // Check if the href matches the current path
        // We handle "index.html" specifically and also exact matches
        if (href === currentPath || (currentPath === "index.html" && href === "./") || (href.includes(currentPath) && currentPath !== "")) {
             link.classList.add("active");
        } else {
             link.classList.remove("active");
        }
    });
}