function copyBoardLink() {
    const link = window.location.href;

    navigator.clipboard.writeText(link).then(() => {
        const msg = document.getElementById("share-msg");
        msg.style.display = "block";

        setTimeout(() => {
            msg.style.display = "none";
        }, 2000);
    });
}


// 🔗 Mobile Native Share (Android Share Sheet)
function shareBoard() {
    const link = window.location.href;

    if (navigator.share) {
        navigator.share({
            title: document.title,
            text: "Check out this Pinterest board!",
            url: link
        })
        .catch(err => console.log("Share cancelled", err));
    } else {
        alert("Sharing not supported on this device. Link copied instead.");
        copyBoardLink();
    }
}
