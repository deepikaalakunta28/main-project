const container = document.getElementById("pin-container");
const trigger = document.getElementById("load-trigger");

let page = 2;
let loading = false;

async function loadMore() {
  if (loading) return;
  loading = true;

  const res = await fetch(`?page=${page}`);
  const html = await res.text();

  // ⛔ Stop when there are no more pages
  if (!html.trim()) {
    observer.disconnect();
    return;
  }

  container.insertAdjacentHTML("beforeend", html);

  page++;
  loading = false;
}

const observer = new IntersectionObserver(entries => {
  if (entries[0].isIntersecting) loadMore();
});

observer.observe(trigger);

