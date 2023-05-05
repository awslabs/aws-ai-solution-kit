// Save configuration in txt2img panel
function getDomValue(selector, defaultValue, isTextContent = false) {
    try {
        const element = document.querySelector(selector);
        if (isTextContent) {
            return element.textContent || defaultValue;
        } else {
            return element.value || defaultValue;
        }
    } catch (error) {
        return defaultValue;
    }
}

function txt2img_config_save() {
    var config = {};

    // now it's all special case under txt2img_settings div element
    scrap_ui_component_value(config);

    // store config in local storage for debugging
    localStorage.setItem("txt2imgConfig", JSON.stringify(config));

    //following code is to get s3 presigned url from middleware and upload the ui parameters
    const key = "config/aigc.json";
    let remote_url = config["aws_api_gateway_url"];
    if (!remote_url.endsWith("/")) {
        remote_url += "/";
    }
    let get_presigned_s3_url = remote_url;
    get_presigned_s3_url += "inference/generate-s3-presigned-url-for-uploading";
    const api_key = config["aws_api_token"];

    const config_presigned_url = getPresignedUrl(
        get_presigned_s3_url,
        api_key,
        key,
        function (error, presignedUrl) {
            if (error) {
                console.error("Error fetching presigned URL:", error);
            } else {
                // console.log("Presigned URL:", presignedUrl);
                const url = presignedUrl.replace(/"/g, "");
                // console.log("url:", url);

                // Upload configuration JSON file to S3 bucket with pre-signed URL
                const config_data = JSON.stringify(config);
                // console.log(config_data)

                put_with_xmlhttprequest(url, config_data)
                    .then((response) => {
                        console.log(response);
                        // Trigger a simple alert after the HTTP PUT has completed
                        alert(
                            "The configuration has been successfully uploaded."
                        );
                        // TODO: meet the cors issue, need to implement it later
                        // let inference_url = remote_url + 'inference/run-sagemaker-inference';
                        // console.log("api-key is ", api_key)
                        // postToApiGateway(inference_url, api_key, config_data, function (error, response) {
                        //     if (error) {
                        //         console.error("Error posting to API Gateway:", error);
                        //     } else {
                        //         console.log("Successfully posted to API Gateway:", response);
                        //         alert("Succeed trigger the remote sagemaker inference.");
                        //         // You can also add an alert or any other action you'd like to perform on success
                        //     }
                        // })
                    })
                    .catch((error) => {
                        console.log(error);
                        alert(
                            "An error occurred while uploading the configuration."
                        );
                    });
            }
        }
    );
}

function scrap_ui_component_value_with_error_handling(config) {
    config["script_txt2txt_xyz_plot_x_values"] = getValue(
        "#script_txt2txt_xyz_plot_x_values > label > textarea"
    );
    config["script_txt2txt_xyz_plot_y_values"] = getValue(
        "#script_txt2txt_xyz_plot_y_values > label > textarea"
    );
    config["script_txt2txt_xyz_plot_z_values"] = getValue(
        "#script_txt2txt_xyz_plot_z_values > label > textarea"
    );
    config["script_txt2txt_prompt_matrix_different_seeds"] = getValue(
        "#script_txt2txt_prompt_matrix_different_seeds > label > input"
    );
    config["script_txt2txt_prompt_matrix_margin_size"] = getValue(
        "#script_txt2txt_prompt_matrix_margin_size > div > div > input"
    );
    config["script_txt2txt_prompt_matrix_put_at_start"] = getValue(
        "#script_txt2txt_prompt_matrix_put_at_start > label > input"
    );
    config["script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate"] =
        getValue(
            "#script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate > label > input"
        );
    config[
        "script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate_batch"
    ] = getValue(
        "#script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate_batch > label > input"
    );
    config["script_txt2txt_xyz_plot_draw_legend"] = getValue(
        "#script_txt2txt_xyz_plot_draw_legend > label > input"
    );
    config["script_txt2txt_xyz_plot_include_lone_images"] = getValue(
        "#script_txt2txt_xyz_plot_include_lone_images > label > input"
    );
    config["script_txt2txt_xyz_plot_include_sub_grids"] = getValue(
        "#script_txt2txt_xyz_plot_include_sub_grids > label > input"
    );
    config["script_txt2txt_xyz_plot_margin_size"] = getValue(
        "#script_txt2txt_xyz_plot_margin_size > div > div > input"
    );
    config["script_txt2txt_xyz_plot_no_fixed_seeds"] = getValue(
        "#script_txt2txt_xyz_plot_no_fixed_seeds > label > input"
    );
    config["txt2img_batch_count"] = getValue(
        "#txt2img_batch_count > div > div > input"
    );
    config["txt2img_batch_size"] = getValue(
        "#txt2img_batch_size > div > div > input"
    );
    config["txt2img_cfg_scale"] = getValue(
        "#txt2img_cfg_scale > div > div > input"
    );
    config["txt2img_denoising_strength"] = getValue(
        "#txt2img_denoising_strength > div > div > input"
    );
    config["txt2img_enable_hr"] = getValue(
        "#txt2img_enable_hr > label > input"
    );
    config["txt2img_height"] = getValue("#txt2img_height > div > div > input");
    config["txt2img_hires_steps"] = getValue(
        "#txt2img_hires_steps > div > div > input"
    );
    config["txt2img_hr_resize_x"] = getValue(
        "#txt2img_hr_resize_x > div > div > input"
    );
    config["txt2img_hr_resize_y"] = getValue(
        "#txt2img_hr_resize_y > div > div > input"
    );
    config["txt2img_hr_scale"] = getValue(
        "#txt2img_hr_scale > div > div > input"
    );
    config["txt2img_restore_faces"] = getValue(
        "#txt2img_restore_faces > label > input"
    );
    config["txt2img_seed"] = getValue("#txt2img_seed > label > input");
    config["txt2img_seed_resize_from_h"] = getValue(
        "#txt2img_seed_resize_from_h > div > div > input"
    );
    config["txt2img_seed_resize_from_w"] = getValue(
        "#txt2img_seed_resize_from_w > div > div > input"
    );
    config["txt2img_steps"] = getValue("#txt2img_steps > div > div > input");
    config["txt2img_style_img"] = getText(
        "#txt2img_style_img > label > textarea"
    );
    config["txt2img_style_img_batch_size"] = getValue(
        "#txt2img_style_img_batch_size > div > div > input"
    );
    config["txt2img_style_img_seed"] = getValue(
        "#txt2img_style_img_seed > label > input"
    );
    config["txt2img_style_img_steps"] = getValue(
        "#txt2img_style_img_steps > div > div > input"
    );
    config["txt2img_style_img_style_strength"] = getValue(
        "#txt2img_style_img_style_strength > div > div > input"
    );
    config["txt2img_style_txt"] = getText(
        "#txt2img_style_txt > label > textarea"
    );
    config["txt2img_style_txt_seed"] = getValue(
        "#txt2img_style_txt_seed > label > input"
    );
    config["txt2img_style_txt_steps"] = getValue(
        "#txt2img_style_txt_steps > div > div > input"
    );
    config["txt2img_style_txt_style_strength"] = getValue(
        "#txt2img_style_txt_style_strength > div > div > input"
    );
    config["txt2img_width"] = getValue("#txt2img_width > div > div > input");
}
function scrap_ui_component_value(config) {
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

    // config["script_list"] = document.querySelector(
    //     "#script_list > label > div > div > span"
    // ).textContent;

    config["script_list"] = document.querySelector("#script_list > label > div > div.wrap-inner.svelte-1g4zxts > div > input").value

    // config["script_txt2txt_xyz_plot_x_type"] = document.querySelector(
    //     "#script_txt2txt_xyz_plot_x_type > label > div > div > span"
    // ).textContent;
    config["script_txt2txt_xyz_plot_x_type"] = document.querySelector("#script_txt2txt_xyz_plot_x_type > label > div > div.wrap-inner.svelte-1g4zxts > div > input").value
    config["script_txt2txt_xyz_plot_x_value"] = document.querySelector("#script_txt2txt_xyz_plot_x_values > label > textarea").value
    // config["script_txt2txt_xyz_plot_y_type"] = document.querySelector(
    //     "#script_txt2txt_xyz_plot_y_type > label > div > div > span"
    // ).textContent;
    config["script_txt2txt_xyz_plot_y_type"]=document.querySelector("#script_txt2txt_xyz_plot_y_type > label > div > div.wrap-inner.svelte-1g4zxts > div > input").value
    config["script_txt2txt_xyz_plot_y_value"]=document.querySelector("#script_txt2txt_xyz_plot_y_values > label > textarea").value
    config["script_txt2txt_xyz_plot_z_type"] = document.querySelector("#script_txt2txt_xyz_plot_z_type > label > div > div.wrap-inner.svelte-1g4zxts > div > input").value
    config["script_txt2txt_xyz_plot_z_value"] = document.querySelector("#script_txt2txt_xyz_plot_z_values > label > textarea").value

    config["txt2img_hr_upscaler"] = document.querySelector(
        "#txt2img_hr_upscaler > label > div > div > div > input"
    ).value;
    config["txt2img_sampling_method"] = document.querySelector("#txt2img_sampling > label > div > div.wrap-inner.svelte-1g4zxts > div > input").value;
    
    config["txt2img_sampling_steps"]=document.querySelector("#txt2img_steps > div.wrap.svelte-1cl284s > div > input")

    //sagemaker endpoint
    config["sagemaker_endpoint"] = document.querySelector("#sagemaker_endpoint_dropdown > label > div > div.wrap-inner.svelte-1g4zxts > div > input").value;
    //stable diffusion checkpoint
    config["sagemaker_stable_diffuion_checkpoint"] = document.querySelector(
        "#stable_diffusion_checkpoint_dropdown > label > div > div.wrap-inner.svelte-1g4zxts > div > input"
    ).value; //stable diffusion checkpoint
    config["stable_diffusion_checkpoint"] = document.querySelector(
        "#stable_diffusion_checkpoint_dropdown > label > div > div.wrap-inner.svelte-1g4zxts > div > input"
    ).value;

    //Textual Inversion
    // config["sagemaker_texual_inversion_model"] = document.querySelector(
    //     "#sagemaker_texual_inversion_dropdown > label > div > div.wrap-inner.svelte-1g4zxts > div > input"
    // ).value;

    // const tokens = document.querySelectorAll("#sagemaker_texual_inversion_dropdown .wrap-inner.svelte-1g4zxts .token > span");
    const wrapInner = document.querySelector("#sagemaker_texual_inversion_dropdown > label > div > div.wrap-inner.svelte-1g4zxts")
    const tokens = wrapInner.querySelectorAll(".token.svelte-1g4zxts");
    const values = [];
    
    tokens.forEach(token => {
      const spanValue = token.querySelector("span.svelte-1g4zxts").textContent;
      values.push(spanValue);
    });
    config["sagemaker_texual_inversion_model"]=values.join(':')
    
    console.log("guming debug>>>")
    console.log(values);
    


    //LoRa
    // config["sagemaker_lora_model"] = document.querySelector(
    //     "#sagemaker_lora_list_dropdown > label > div > div.wrap-inner.svelte-1g4zxts > div > input"
    // ).value;

    const wrapInner1 = document.querySelector("#sagemaker_lora_list_dropdown > label > div > div.wrap-inner.svelte-1g4zxts")
    const tokens1 = wrapInner1.querySelectorAll(".token.svelte-1g4zxts");
    const values1 = [];
    
    tokens1.forEach(token => {
      const spanValue = token.querySelector("span.svelte-1g4zxts").textContent;
      values1.push(spanValue);
    });
    config["sagemaker_lora_model"] = values1.join(':')
    console.log(values1);


    //HyperNetwork
    // config["sagemaker_hypernetwork_model"] = document.querySelector(
    //     "#sagemaker_hypernetwork_dropdown > label > div > div.wrap-inner.svelte-1g4zxts > div > input"
    // ).value;

    // document.querySelector("#sagemaker_hypernetwork_dropdown > label > div > div.wrap-inner.svelte-1g4zxts")
    // const wrapInner2 = document.querySelector("#sagemaker_hypernetwork_dropdown > label > div > div.wrap-inner.svelte-1g4zxts")
    const wrapInner2 = document.querySelector("#sagemaker_hypernetwork_dropdown > label > div > div.wrap-inner.svelte-1g4zxts")
    const tokens2 = wrapInner2.querySelectorAll(".token.svelte-1g4zxts");
    const values2 = [];
    
    tokens2.forEach(token => {
      const spanValue = token.querySelector("span.svelte-1g4zxts").textContent;
      values2.push(spanValue);
    });
    config["sagemaker_hypernetwork_model"] = values2.join(':')
    console.log(values2);

    //ControlNet model
    // config["sagemaker_controlnet_model"] = document.querySelector(
    //     "#sagemaker_controlnet_model_dropdown > label > div > div.wrap-inner.svelte-1g4zxts > div > input"
    // ).value;
    
    const wrapInner3 = document.querySelector("#sagemaker_controlnet_model_dropdown > label > div > div.wrap-inner.svelte-1g4zxts")
    const tokens3 = wrapInner3.querySelectorAll(".token.svelte-1g4zxts");
    const values3 = [];
    
    tokens3.forEach(token => {
      const spanValue = token.querySelector("span.svelte-1g4zxts").textContent;
      values3.push(spanValue);
    });
    config["sagemaker_controlnet_model"] = values3.join(':')
    console.log(values3);

    //control net part parameter
    config["txt2img_controlnet_ControlNet_input_image"] =
        document.querySelector(
            "#txt2img_controlnet_ControlNet_input_image > div.svelte-rlgzoo.fixed-height > div > img"
        );
    config["controlnet_enable"] = document.querySelector(
        "#component-200 > label > input"
    ).checked;

    // document.querySelector("#component-200 > label > input")

    config["controlnet_lowVRAM_enable"] = document.querySelector(
        "#component-201 > label > input"
    ).checked;
    config["controlnet_pixel_perfect"] = document.querySelector(
        "#component-203 > label > input"
    ).checked;
    
    config["controlnet_allow_preview"] = document.querySelector("#txt2img_controlnet_ControlNet_preprocessor_preview > label > input").checked
   
    config["controlnet_preprocessor"] = document.querySelector("#component-206 > label > div > div.wrap-inner.svelte-1g4zxts > div > input").value
    config["controlnet_model"] = document.querySelector("#component-208 > label > div > div.wrap-inner.svelte-1g4zxts > div > input").value
    config["control_weight"] = document.querySelector(
        "#component-213 > div.wrap.svelte-1cl284s > div > input"
    ).value;
    // document.querySelector("#component-213 > div.wrap.svelte-1cl284s > div > input")
    config["controlnet_starting_control_step"] = document.querySelector(
        "#component-214 > div.wrap.svelte-1cl284s > div > input"
    ).value;
    config["controlnet_ending_control_step"] = document.querySelector(
        "#component-215 > div.wrap.svelte-1cl284s > div > input"
    ).value;
    config["controlnet_control_mode(guess_mode)"] = document.querySelector(
        "#component-222 > div.wrap.svelte-1p9xokt > label.svelte-1p9xokt.selected > input"
    ).value;
    config["controlnet_resize_mode"] = document.querySelector(
        "#component-223 > div.wrap.svelte-1p9xokt > label:nth-child(1) > input"
    ).value;
    config[
        "controlnet_loopback_automatically_send_generated_images_to_this_controlnet_unit"
    ] = document.querySelector("#component-224 > label > input").value;

    config["script_txt2txt_prompt_matrix_prompt_type_positive"] =
        document.querySelector(
            "#script_txt2txt_prompt_matrix_prompt_type > div.wrap.svelte-1p9xokt > label.svelte-1p9xokt.selected > input"
        ).value;
    config["script_txt2txt_prompt_matrix_prompt_type_negative"] =
        document.querySelector(
            "#script_txt2txt_prompt_matrix_prompt_type > div.wrap.svelte-1p9xokt > label:nth-child(2) > input"
        ).value;
    config["script_txt2txt_prompt_matrix_variations_delimiter_comma"] =
        document.querySelector(
            "#script_txt2txt_prompt_matrix_variations_delimiter > div.wrap.svelte-1p9xokt > label.svelte-1p9xokt.selected > input"
        ).value;
    config["script_txt2txt_prompt_matrix_variations_delimiter_comma"] =
        document.querySelector(
            "#script_txt2txt_prompt_matrix_variations_delimiter > div.wrap.svelte-1p9xokt > label:nth-child(2) > input"
        ).value;
    config["script_txt2txt_prompt_matrix_margin_size"] = document.querySelector(
        "#script_txt2txt_prompt_matrix_margin_size > div.wrap.svelte-1cl284s > div > input"
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
    config["script_txt2txt_prompts_from_file_or_textbox_prompt_txt"] =
        document.querySelector(
            "#script_txt2txt_prompts_from_file_or_textbox_prompt_txt > label > textarea"
        ).value;
    config["script_txt2txt_prompts_from_file_or_textbox_file"] =
        document.querySelector(
            "#script_txt2txt_prompts_from_file_or_textbox_file > div.svelte-116rqfv.center.boundedheight.flex > div"
        );

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
        "#aws_middleware_api > label > textarea"
    ).value;

    config["aws_api_token"] = document.querySelector(
        "#aws_middleware_token > label > textarea"
    ).value;
}

function put_with_xmlhttprequest(config_url, config_data) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
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
            callback(null, xhr.responseText);
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

function postToApiGateway(remote_url, api_key, data, callback) {
    const apiUrl = remote_url;

    const xhr = new XMLHttpRequest();
    xhr.open("POST", apiUrl, true);
    // xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("x-api-key", api_key);

    xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 400) {
            callback(null, xhr.responseText);
        } else {
            callback(
                new Error(`Error posting to API Gateway: ${xhr.statusText}`),
                null
            );
        }
    };

    xhr.onerror = function () {
        callback(new Error("Error posting to API Gateway"), null);
    };

    // Convert data object to JSON string before sending
    xhr.send(JSON.stringify(data));
}
