let nextPage = 2;

document.addEventListener("htmx:afterSwap", () => {
    const loader = document.getElementById("load-more");
    if (!loader) return;

    loader.setAttribute("hx-get", `?page=${nextPage}`);
    nextPage += 1;
});
