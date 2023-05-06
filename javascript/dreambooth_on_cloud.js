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

function check_create_model_params() {
    console.log(arguments)
    var re = /^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,30}$/;
    console.log(re.exec(arguments[0]))
    if (arguments[0] == "") {
        do_save = alert("Please add a model name.");
    }
    else if (arguments[1] == "") {
        do_save = alert("Please select a checkpoint");
    }
    else if (re.exec(arguments[0]) == null) {
        do_save = alert("Please change another model name");
    }
    let filtered_args = filterArgs(8, arguments);
    console.log(arguments)
    return filtered_args
    // return arguments
}