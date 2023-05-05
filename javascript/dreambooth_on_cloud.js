// Sagemaker Train!
function db_start_sagemaker_train() {
    // let db_model_panel = document.getElementById("ModelPanel");
    // console.log(db_model_panel.children[0].children[1].children[1].children[0].children[0].children[0].children[0].getElementsByTagName("label")[0].children[1].children[0].children[0].children[0]);
    // db_model_name = db_model_panel.children[0].children[1].children[1].children[0].children[0].children[0].children[0].getElementsByTagName("label")[0].children[1].children[0].children[0].children[0];
    // // db_model_name = db_model_panel.children[0].children[1].children[1].children[0].children[0].children[0].children[0].getElementsByTagName("label")[0];
    // db_model_name.value = "xxxx"
    console.log("Sagemaker training");
    console.log(arguments);
    // db_model_name.dispatchEvent(new Event('change'))
    save_config();
    // let sagemaker_train = gradioApp().getElementById("db_sagemaker_train");
    // sagemaker_train.style.display = "block";
    return filterArgs(2, arguments);
}