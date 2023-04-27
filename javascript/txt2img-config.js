// Save configuration in txt2img panel
function txt2img_config_save() {
    var config = {};
    // list of input elements to save
    // step 1: copy html elements from browser with filter "txt2img_settings"
    // step 2: extract div id from save html with command "grep -oP '(?<=<div id=")[^"]*' txt2img_settings.html | grep -v "component" | awk '{print "\"" $0 "\","}' | sort | uniq", 50 in total for now
    // step 3: handle special cases for textarea and ignore empty elements with comments below

    // element with "input class", it's now obsolete due to upstream changes, we need to handle all input elements as special case
    var params_save_input = [
        // "axis_options",
        // "gallery",
        // "sampler_selection_txt2img",
        // "script_txt2txt_prompt_matrix_different_seeds",
        // "script_txt2txt_prompt_matrix_margin_size",
        // "script_txt2txt_prompt_matrix_put_at_start",
        // "script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate",
        // "script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate_batch",
        // "script_txt2txt_prompts_from_file_or_textbox_file",
        // "script_txt2txt_prompts_from_file_or_textbox_prompt_txt",
        // "script_txt2txt_xyz_plot_draw_legend",
        // "script_txt2txt_xyz_plot_include_lone_images",
        // "script_txt2txt_xyz_plot_include_sub_grids",
        // "script_txt2txt_xyz_plot_margin_size",
        // "script_txt2txt_xyz_plot_no_fixed_seeds",
        // "script_txt2txt_xyz_plot_x_values",
        // "script_txt2txt_xyz_plot_y_values",
        // "script_txt2txt_xyz_plot_z_values",
        // "swap_axes",
        // "txt2img_batch_count",
        // "txt2img_batch_size",
        // "txt2img_cfg_scale",
        // "txt2img_column_batch",
        // "txt2img_column_size",
        // "txt2img_denoising_strength",
        // "txt2img_dimensions_row",
        // "txt2img_enable_hr",
        // "txt2img_height",
        // "txt2img_hires_fix",
        // "txt2img_hires_fix_row1",
        // "txt2img_hires_fix_row2",
        // "txt2img_hires_steps",
        // "txt2img_hr_resize_x",
        // "txt2img_hr_resize_y",
        // "txt2img_hr_scale",
        // "txt2img_override_settings",
        // "txt2img_override_settings_row",
        // "txt2img_restore_faces",
        // "txt2img_script_container",
        // "txt2img_seed",
        // "txt2img_seed_resize_from_h",
        // "txt2img_seed_resize_from_w",
        // "txt2img_override_settings_row",
        // "txt2img_settings",
        // "txt2img_steps",
        // "txt2img_subseed",
        // "txt2img_subseed_row",
        // "txt2img_subseed_show",
        // "txt2img_subseed_show_box",
        // "txt2img_subseed_strength",
        // "txt2img_tiling",
        // "txt2img_width",
        // "txtimg_hr_finalres",
    ];
    // element with "select class"
    var params_save_select = [
        // "script_list",
        // "script_txt2txt_xyz_plot_x_type",
        // "script_txt2txt_xyz_plot_y_type",
        // "script_txt2txt_xyz_plot_z_type",
        // "txt2img_hr_upscaler",
        // "txt2img_sampling"
    ];

    // iterate through all input elements list
    for (var i = 0; i < params_save_input.length; i++) {
        var element = params_save_input[i];
        console.log("iterating through input elements: " + element);
        // skip if element value is empty
        if (
            document
                .querySelector("body > gradio-app")
                .shadowRoot.getElementById(element)
                .querySelector("input").value == ""
        ) {
            console.log("skipping empty element: " + element);
            continue;
        }
        element_val = document
            .querySelector("body > gradio-app")
            .shadowRoot.getElementById(element)
            .querySelector("input").value;
        // store key value pair in config
        config[element] = element_val;
    }

    // iterate through all select elements
    for (var i = 0; i < params_save_select.length; i++) {
        var element = params_save_select[i];
        console.log("iterating through select elements: " + element);
        // skip if element value is empty
        if (
            document
                .querySelector("body > gradio-app")
                .shadowRoot.getElementById(element)
                .querySelector("select").value == ""
        ) {
            console.log("skipping empty element: " + element);
            continue;
        }
        element_val = document
            .querySelector("body > gradio-app")
            .shadowRoot.getElementById(element)
            .querySelector("select").value;
        // store key value pair in config
        config[element] = element_val;
    }

    // now it's all special case under txt2img_settings div element
    config["script_txt2txt_xyz_plot_x_values"] = document.querySelector(
        "#script_txt2txt_xyz_plot_x_values > label > textarea"
    ).value;
    config["script_txt2txt_xyz_plot_y_values"] = document.querySelector(
        "#script_txt2txt_xyz_plot_y_values > label > textarea"
    ).value;
    config["script_txt2txt_xyz_plot_z_values"] = document.querySelector(
        "#script_txt2txt_xyz_plot_z_values > label > textarea"
    ).value;
    config["script_txt2txt_prompt_matrix_different_seeds"] =
        document.querySelector(
            "#script_txt2txt_prompt_matrix_different_seeds > label > input"
        ).value;
    config["script_txt2txt_prompt_matrix_margin_size"] = document.querySelector(
        "#script_txt2txt_prompt_matrix_margin_size > div > div > input"
    ).value;
    config["script_txt2txt_prompt_matrix_put_at_start"] =
        document.querySelector(
            "#script_txt2txt_prompt_matrix_put_at_start > label > input"
        ).value;
    config["script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate"] =
        document.querySelector(
            "#script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate > label > input"
        ).value;
    config[
        "script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate_batch"
    ] = document.querySelector(
        "#script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate_batch > label > input"
    ).value;
    config["script_txt2txt_xyz_plot_draw_legend"] = document.querySelector(
        "#script_txt2txt_xyz_plot_draw_legend > label > input"
    ).value;
    config["script_txt2txt_xyz_plot_include_lone_images"] =
        document.querySelector(
            "#script_txt2txt_xyz_plot_include_lone_images > label > input"
        ).value;
    config["script_txt2txt_xyz_plot_include_sub_grids"] =
        document.querySelector(
            "#script_txt2txt_xyz_plot_include_sub_grids > label > input"
        ).value;
    config["script_txt2txt_xyz_plot_margin_size"] = document.querySelector(
        "#script_txt2txt_xyz_plot_margin_size > div > div > input"
    ).value;
    config["script_txt2txt_xyz_plot_no_fixed_seeds"] = document.querySelector(
        "#script_txt2txt_xyz_plot_no_fixed_seeds > label > input"
    ).value;
    config["txt2img_batch_count"] = document.querySelector(
        "#txt2img_batch_count > div > div > input"
    ).value;
    config["txt2img_batch_size"] = document.querySelector(
        "#txt2img_batch_size > div > div > input"
    ).value;
    config["txt2img_cfg_scale"] = document.querySelector(
        "#txt2img_cfg_scale > div > div > input"
    ).value;
    config["txt2img_denoising_strength"] = document.querySelector(
        "#txt2img_denoising_strength > div > div > input"
    ).value;
    config["txt2img_enable_hr"] = document.querySelector(
        "#txt2img_enable_hr > label > input"
    ).value;
    config["txt2img_height"] = document.querySelector(
        "#txt2img_height > div > div > input"
    ).value;
    config["txt2img_hires_steps"] = document.querySelector(
        "#txt2img_hires_steps > div > div > input"
    ).value;
    config["txt2img_hr_resize_x"] = document.querySelector(
        "#txt2img_hr_resize_x > div > div > input"
    ).value;
    config["txt2img_hr_resize_y"] = document.querySelector(
        "#txt2img_hr_resize_y > div > div > input"
    ).value;
    config["txt2img_hr_scale"] = document.querySelector(
        "#txt2img_hr_scale > div > div > input"
    ).value;
    config["txt2img_restore_faces"] = document.querySelector(
        "#txt2img_restore_faces > label > input"
    ).value;
    config["txt2img_seed"] = document.querySelector(
        "#txt2img_seed > label > input"
    ).value;
    config["txt2img_seed_resize_from_h"] = document.querySelector(
        "#txt2img_seed_resize_from_h > div > div > input"
    ).value;
    config["txt2img_seed_resize_from_w"] = document.querySelector(
        "#txt2img_seed_resize_from_w > div > div > input"
    ).value;
    config["txt2img_steps"] = document.querySelector(
        "#txt2img_steps > div > div > input"
    ).value;
    config["txt2img_subseed"] = document.querySelector(
        "#txt2img_subseed > label > input"
    ).value;
    // config['txt2img_subseed_row'] = document.querySelector("#txt2img_subseed_row > label > input").value
    config["txt2img_subseed_show"] = document.querySelector(
        "#txt2img_subseed_show > label > input"
    ).value;
    config["txt2img_subseed_strength"] = document.querySelector(
        "#txt2img_subseed_strength > div > div > input"
    ).value;
    config["txt2img_tiling"] = document.querySelector(
        "#txt2img_tiling > label > input"
    ).value;
    config["txt2img_width"] = document.querySelector(
        "#txt2img_width > div > div > input"
    ).value;

    config["script_list"] = document.querySelector(
        "#script_list > label > div > div > span"
    ).textContent;
    config["script_txt2txt_xyz_plot_x_type"] = document.querySelector(
        "#script_txt2txt_xyz_plot_x_type > label > div > div > span"
    ).textContent;
    config["script_txt2txt_xyz_plot_y_type"] = document.querySelector(
        "#script_txt2txt_xyz_plot_y_type > label > div > div > span"
    ).textContent;
    config["script_txt2txt_xyz_plot_z_type"] = document.querySelector(
        "#script_txt2txt_xyz_plot_z_type > label > div > div > span"
    ).textContent;

    config["txt2img_hr_upscaler"] = document.querySelector(
        "#txt2img_hr_upscaler > label > div > div > div > input"
    ).value;
    config["txt2img_sampling"] = document.querySelector(
        "#txt2img_sampling > label > div > div > span"
    ).textContent;

    // config for prompt area
    config["txt2img_prompt"] = document.querySelector(
        "#txt2img_prompt > label > textarea"
    ).value;
    config["txt2img_neg_prompt"] = document.querySelector(
        "#txt2img_neg_prompt > label > textarea"
    ).value;
    config["txt2img_styles"] = document.querySelector(
        "#txt2img_styles > label > div > div > div > input"
    ).value;

    // get the api-gateway url and token
    config["aws_api_gateway_url"] = document.querySelector(
        "#component-1298 > label > textarea"
    ).value;
    config["aws_api_token"] = document.querySelector(
        "#component-1299 > label > textarea"
    ).value;

    // store config in local storage for debugging
    localStorage.setItem("txt2imgConfig", JSON.stringify(config));

    const key = "aigc.json";
    const remote_url =
        config["aws_api_gateway_url"] +
        "inference/generate-s3-presigned-url-for-uploading";
    const api_key = config["aws_api_token"];

    const config_presigned_url = getPresignedUrl(
        remote_url,
        api_key,
        key,
        function (error, presignedUrl) {
            if (error) {
                console.error("Error fetching presigned URL:", error);
            } else {
                console.log("Presigned URL:", presignedUrl);
                // Upload configuration JSON file to S3 bucket with pre-signed URL
                const config_data = JSON.stringify(config);
                console.log(config_data)

                put_with_xmlhttprequest(presignedUrl, config_data)
                    .then((response) => {
                        console.log(response);
                    })
                    .catch((error) => {
                        console.log(error);
                    });
            }
        }
    );

    // store as config file in local directory
    // var config_file = "txt2imgConfig.json";
    // var a = document.createElement('a');
    // a.download = config_file;
    // a.style.display = 'none';
    // var blob = new Blob([config_data], {type: "application/json"});
    // a.href = URL.createObjectURL(blob);
    // document.body.appendChild(a);
    // a.click();
    // document.body.removeChild(a);
}

// function put_with_xmlhttprequest(url, data) {
//     return new Promise((resolve, reject) => {
//         const xhr = new XMLHttpRequest();
//         xhr.open("PUT", url);
//         xhr.setRequestHeader("Content-Length", new Blob([data]).size);
//         xhr.onload = () => {
//             resolve(xhr.responseText);
//         };
//         xhr.onerror = () => {
//             reject(xhr.statusText);
//         };
//         xhr.send(data);
//     });
// }

function put_with_xmlhttprequest(config_url, config_data) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        console.log(`guming debug>> config_url is ${config_url}`)
        xhr.open("PUT", config_url, true);
        //   xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve(xhr.responseText);
                } else {
                    reject(xhr.statusText);
                }
            }
        };

        xhr.onerror = () => {
            reject("Network error");
        };

        xhr.send(config_data);
    });
}

function getPresignedUrl(remote_url, api_key, key, callback) {
    const apiUrl = remote_url;
    const queryParams = new URLSearchParams({
        key: key,
    });

    const xhr = new XMLHttpRequest();
    xhr.open("GET", `${apiUrl}?${queryParams}`, true);
    xhr.setRequestHeader("x-api-key", api_key);

    xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 400) {
            callback(null, xhr.responseText);;
        } else {
            callback(
                new Error(`Error fetching presigned URL: ${xhr.statusText}`),
                null
            );
        }
    };

    xhr.onerror = function () {
        callback(new Error("Error fetching presigned URL"), null);
    };

    xhr.send();
}
