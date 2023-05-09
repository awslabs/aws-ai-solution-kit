// pop up window for inference reminder
function generate_on_cloud(){    
    console.log("Inference started.");
    document.querySelector("#html_log_txt2img").innerHTML = "Inference started. Please wait...";
    return null;
}

function sagemaker_model_update(){
    console.log("Model update started.");
    document.querySelector("#html_log_txt2img").innerHTML = "Model update started. Please wait...";
    return null;
}

function sagemaker_deploy_endpoint(){
    res = confirm("You are about to deploy an endpoint. This will take a few minutes. Do you want to continue?");
    if (res === true) {
        console.log("Endpoint deployment started.");
        document.querySelector("#html_log_txt2img").innerHTML = "Endpoint deployment started. Please wait...";
    } else {
        console.log("Endpoint deployment cancelled.");
        document.querySelector("#html_log_txt2img").innerHTML = "Endpoint deployment cancelled.";
    }
    return null;
}

function update_auth_settings(){
    res = confirm("You are about to update authentication settings. Do you want to continue?");
    if (res === true) {
        console.log("Settings updated.");
    } else {
        console.log("Settings update cancelled.");
    }
    return null;
}