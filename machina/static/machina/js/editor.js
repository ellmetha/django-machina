var MachinaMarkdownEditor = MachinaMarkdownEditor | {};

MachinaMarkdownEditor = (function() {
  var isMarkdownTextarea = function(el) {
    return (' ' + el.className + ' ').indexOf(' machina-mde-markdown ') > -1;
  };

  var createEditor = function(el) {
    new EasyMDE({
      element: el,
      hideIcons: ['preview', 'guide', 'side-by-side', 'fullscreen', ],
      renderingConfig: {
        singleLineBreaks: false
      },
      spellChecker: false,
    });
  };

  var init = function() {
    elements = document.getElementsByTagName("textarea");
    for (var i = 0; i < elements.length; ++i){
      if (isMarkdownTextarea(elements[i])) {
        createEditor(elements[i]);
      }
    }
  };

  return {
    init: function() {
      return init();
    },
  };
})();

window.onload = MachinaMarkdownEditor.init;
