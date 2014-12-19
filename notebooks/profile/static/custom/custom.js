// leave at least 2 line with only a star on it below, or doc generation fails
/**
 *
 *
 * Placeholder for custom user javascript
 * mainly to be overridden in profile/static/custom/custom.js
 * This will always be an empty file in IPython
 *
 * User could add any javascript in the `profile/static/custom/custom.js` file
 * (and should create it if it does not exist).
 * It will be executed by the ipython notebook at load time.
 *
 * Same thing with `profile/static/custom/custom.css` to inject custom css into the notebook.
 *
 * Example :
 *
 * Create a custom button in toolbar that execute `%qtconsole` in kernel
 * and hence open a qtconsole attached to the same kernel as the current notebook
 *
 *    $([IPython.events]).on('app_initialized.NotebookApp', function(){
 *        IPython.toolbar.add_buttons_group([
 *            {
 *                 'label'   : 'run qtconsole',
 *                 'icon'    : 'icon-terminal', // select your icon from http://fortawesome.github.io/Font-Awesome/icons
 *                 'callback': function () {
 *                     IPython.notebook.kernel.execute('%qtconsole')
 *                 }
 *            }
 *            // add more button here if needed.
 *            ]);
 *    });
 *
 * Example :
 *
 *  Use `jQuery.getScript(url [, success(script, textStatus, jqXHR)] );`
 *  to load custom script into the notebook.
 *
 *    // to load the metadata ui extension example.
 *    $.getScript('/static/notebook/js/celltoolbarpresets/example.js');
 *    // or
 *    // to load the metadata ui extension to control slideshow mode / reveal js for nbconvert
 *    $.getScript('/static/notebook/js/celltoolbarpresets/slideshow.js');
 *
 *
 * @module IPython
 * @namespace IPython
 * @class customjs
 * @static
 */

IPython.Cell.options_default.cm_config.indentUnit = 2;

$([IPython.events]).on('app_initialized.NotebookApp', function(){
  var restartAndRunAll = function(){
                                     console.log('inner1')
                                     IPython.notebook.kernel.restart();
                                     waitAndRunAll(50)
                                   }
  var waitAndRunAll = function(x){
                                   try
                                   {
                                     if (IPython.notebook.kernel.shell_channel.readyState == 1)
                                     {
                                       IPython.notebook.execute_all_cells();
                                       return
                                     }
                                   }
                                   catch (e)
                                   {
                                   }
                                   if(x>1)
                                   {
                                     setTimeout(function() {waitAndRunAll(x-1);}, 100)
                                   }
                                   return
                                 }  

  IPython.toolbar.add_buttons_group([
    {
      'label'   : 'Restart and run all',
      'icon'    : 'icon-undo', // select your icon from http://fortawesome.github.io/Font-Awesome/icons
      'callback': restartAndRunAll
    }
    // add more button here if needed.
  ]);
});