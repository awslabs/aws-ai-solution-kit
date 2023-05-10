// pop up window for inference reminder
function generate_on_cloud(sagemaker_endpoint){
    console.log("Inference started with input: " + sagemaker_endpoint);
    document.querySelector("#html_log_txt2img").innerHTML = "Inference started. Please wait...";
    return [sagemaker_endpoint];
}

function model_update(sd_checkpoints_path, textual_inversion_path, lora_path, hypernetwork_path, controlnet_model_path){
    console.log("Model update started with input: " + sd_checkpoints_path + ", " + textual_inversion_path + ", " + lora_path + ", " + hypernetwork_path + ", " + controlnet_model_path);
    document.querySelector("#html_log_txt2img").innerHTML = "Model update started. Please wait...";
    return [sd_checkpoints_path, textual_inversion_path, lora_path, hypernetwork_path, controlnet_model_path];
}

function deploy_endpoint(instance_type_dropdown, instance_count_textbox){
    console.log("Endpoint deployment started with input: " + instance_type_dropdown + ", " + instance_count_textbox);
    document.querySelector("#html_log_txt2img").innerHTML = "Endpoint deployment started. Please wait...";
    return [instance_type_dropdown, instance_count_textbox];
}

function update_auth_settings(api_url_textbox, api_token_textbox){
    console.log("Settings update started with input: " + api_url_textbox + ", " + api_token_textbox)
    res = confirm("You are about to update authentication settings. Do you want to continue?");
    if (res === true) {
        console.log("Settings updated.");
    } else {
        console.log("Settings update cancelled.");
    }
    return [api_url_textbox, api_token_textbox];
}