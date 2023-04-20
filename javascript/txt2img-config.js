// Save configuration in txt2img panel
function txt2img_config_save(){
    var config = {};
    // list of input elements to save
    // step 1: copy html elements from browser with filter "txt2img_settings" 
    // step 2: extract div id from save html with command "grep -oP '(?<=<div id=")[^"]*' txt2img_settings.html | grep -v "component" | awk '{print "\"" $0 "\","}' | sort | uniq", 50 in total for now
    // step 3: handle special cases for textarea and ignore empty elements with comments below
    
    // element with "input class"
    var params_save_input = [
        // "gallery",
        "script_txt2txt_prompt_matrix_different_seeds",
        "script_txt2txt_prompt_matrix_margin_size",
        "script_txt2txt_prompt_matrix_put_at_start",
        "script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate",
        "script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate_batch",
        // "script_txt2txt_prompts_from_file_or_textbox_file",
        // "script_txt2txt_prompts_from_file_or_textbox_prompt_txt",
        "script_txt2txt_xyz_plot_draw_legend",
        "script_txt2txt_xyz_plot_include_lone_images",
        "script_txt2txt_xyz_plot_include_sub_grids",
        "script_txt2txt_xyz_plot_margin_size",
        "script_txt2txt_xyz_plot_no_fixed_seeds",
        // "script_txt2txt_xyz_plot_x_values",
        // "script_txt2txt_xyz_plot_y_values",
        // "script_txt2txt_xyz_plot_z_values",
        "txt2img_batch_count",
        "txt2img_batch_size",
        "txt2img_cfg_scale",
        "txt2img_column_batch",
        "txt2img_column_size",
        "txt2img_denoising_strength",
        "txt2img_enable_hr",
        "txt2img_height",
        "txt2img_hires_fix",
        "txt2img_hires_steps",
        "txt2img_hr_resize_x",
        "txt2img_hr_resize_y",
        "txt2img_hr_scale",
        // "txt2img_override_settings",
        "txt2img_restore_faces",
        // "txt2img_script_container",
        "txt2img_seed",
        "txt2img_seed_resize_from_h",
        "txt2img_seed_resize_from_w",
        "txt2img_settings",
        "txt2img_steps",
        "txt2img_subseed",
        "txt2img_subseed_show",
        "txt2img_subseed_show_box",
        "txt2img_subseed_strength",
        "txt2img_tiling",
        "txt2img_width",
        // "txtimg_hr_finalres",
    ]
    // element with "select class"
    var params_save_select = [
        "script_list",
        "script_txt2txt_xyz_plot_x_type",
        "script_txt2txt_xyz_plot_y_type",
        "script_txt2txt_xyz_plot_z_type",
        "txt2img_hr_upscaler",
        "txt2img_sampling"
    ]

    // iterate through all input elements list
    for (var i = 0; i < params_save_input.length; i++) {
        var element = params_save_input[i];
        console.log("iterating through input elements: " + element);
        // skip if element value is empty
        if (document.querySelector("body > gradio-app").shadowRoot.getElementById(element).querySelector("input").value == "") {
            console.log("skipping empty element: " + element);
            continue;
        }
        element_val = document.querySelector("body > gradio-app").shadowRoot.getElementById(element).querySelector("input").value
        // store key value pair in config
        config[element] = element_val;
    }
    
    // iterate through all select elements
    for (var i = 0; i < params_save_select.length; i++) {
        var element = params_save_select[i];
        console.log("iterating through select elements: " + element);
        // skip if element value is empty
        if (document.querySelector("body > gradio-app").shadowRoot.getElementById(element).querySelector("select").value == "") {
            console.log("skipping empty element: " + element);
            continue;
        }
        element_val = document.querySelector("body > gradio-app").shadowRoot.getElementById(element).querySelector("select").value
        // store key value pair in config
        config[element] = element_val;
    }

    // special case for textarea
    config['script_txt2txt_xyz_plot_x_values'] = document.querySelector("body > gradio-app").shadowRoot.querySelector("#script_txt2txt_xyz_plot_x_values > label > textarea").value
    config['script_txt2txt_xyz_plot_y_values'] = document.querySelector("body > gradio-app").shadowRoot.querySelector("#script_txt2txt_xyz_plot_y_values > label > textarea").value
    config['script_txt2txt_xyz_plot_z_values'] = document.querySelector("body > gradio-app").shadowRoot.querySelector("#script_txt2txt_xyz_plot_z_values > label > textarea").value

    // store config in local storage for debugging
    localStorage.setItem("txt2imgConfig", JSON.stringify(config));
    
    // create a new config file and store in local directory
    var config_file = "txt2imgConfig.json";
    var config_data = JSON.stringify(config);
    var a = document.createElement('a');
    a.download = config_file;
    a.style.display = 'none';
    var blob = new Blob([config_data], {type: "application/json"});
    a.href = URL.createObjectURL(blob);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

