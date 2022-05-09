window.addEventListener('load', (event) => {
    const script = document.createElement("script");
    script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js';
    script.type = 'text/javascript';
    script.addEventListener('load', () => {
        var all = $(".opblock-summary-control").map(function () {
            $(this).click(function () {
                const DisableTryItOutPlugin = function () {
                    return {
                        statePlugins: {
                            spec: {
                                wrapSelectors: {
                                    allowTryItOutFor: () => () => false
                                }
                            }
                        }
                    }
                }
                alert(typeof window.SwaggerUIBundle.plugins);
                window.SwaggerUIBundle.plugins = null;
                // $('opblock-summary-control').remove();
                var all = $(".try-out").map(function () {
                    $('opblock-summary-control').remove();
                }).get();
            });
        }).get();

        // setInterval(function(){ 
        //     // stuff needs to be done
        //     var all = $(".try-out").map(function () {
        //         $(this).remove();
        //     }).get();
        //   }, 1);


        var r = $('<input type="button" class="btn authorize unlocked" value="AWS IAM" />');
        $('.auth-wrapper').append(r);

        var d = $('<div class="modal-ux-inner"><div class="modal-ux-header"><h3>AWS IAM</h3><button type="button" class="close-modal"><svg width="20" height="20"><use href="#close" xlink:href="#close"></use></svg></button></div><div class="modal-ux-content"><div class="auth-container"><form><div><div class="wrapper"><label>aws_access_key_id:</label><section class=""><input type="text"></section><label>aws_secret_access_key:</label><section class=""><input type="text"></section></div></div></div><div class="auth-btn-wrapper"><button type="submit" class="btn modal-btn auth authorize button">Authorize</button><button class="btn modal-btn auth btn-done button">Close</button></div></form></div></div>');
        // $('.auth-wrapper').append(d);
        const DisableTryItOutPlugin = function () {
            return {
                statePlugins: {
                    spec: {
                        wrapSelectors: {
                            allowTryItOutFor: () => () => false
                        }
                    }
                }
            }
        }
        // alert(window.SwaggerUIBundle)
        $('.modal-dialog-ux').replaceWith(d)

        // alert($element)
        // use jQuery below
    });
    document.head.appendChild(script);
    // https://sdk.amazonaws.com/js/aws-sdk-2.7.20.min.js
});