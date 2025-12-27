document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript is connected!");

    const title = document.getElementById("title");
    title.addEventListener("click", function () {
        alert("You clicked the title!");
    });
});
