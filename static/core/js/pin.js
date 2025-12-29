function copyPinLink() {
    const url = window.location.href;

    navigator.clipboard.writeText(url).then(function () {
        const msg = document.getElementById("copy-msg");
        if (!msg) return;

        msg.style.display = "block";

        setTimeout(() => {
            msg.style.display = "none";
        }, 2000);
    });
}





function getPinShareData() {
    return {
        url: window.location.href,
        title: document.title
    };
}

// WhatsApp Share
function shareWhatsApp() {
    const { url, title } = getPinShareData();
    window.open(`https://wa.me/?text=${encodeURIComponent(title + " " + url)}`);
}

// Telegram Share
function shareTelegram() {
    const { url, title } = getPinShareData();
    window.open(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`);
}

// Twitter / X Share
function shareTwitter() {
    const { url, title } = getPinShareData();
    window.open(`https://twitter.com/share?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`);
}

// Email Share
function shareEmail() {
    const { url, title } = getPinShareData();
    window.location = `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(url)}`;
}
