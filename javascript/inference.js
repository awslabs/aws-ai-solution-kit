// pop up window for inference reminder
function generate_on_cloud(){    
    res = confirm("You are about to run inference on the cloud. This will take a few minutes. Do you want to continue?");
    if (res === true) {
        console.log("Inference started.");
        document.querySelector("#html_log_txt2img").innerHTML = "Inference started. Please wait...";
    } else {
        console.log("Inference cancelled.");
    }
    return null;
}