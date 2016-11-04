var machina = (function(m, $) {

  function cloneFormset(selector, type) {
    var new_element = $(selector).clone(true);
    var total = $('#id_' + type + '-TOTAL_FORMS').val();

    new_element.find(':input').each(function() {
      // update the name and id of the input field
      var new_name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
      $(this).attr('name', new_name);
      var new_id = $(this).attr('id').replace('-' + (total-1) + '-','-' + total + '-');
      $(this).attr('id', new_id);
      $(this).parent('label').attr('for', new_id);
      $(this).prev('label').attr('for', new_id);
      if ($(this).is(':checkbox')) {
        $(this).attr('checked', false);
      }
      else {
        $(this).attr('value', '');
        $(this).val('');
      }
    });
    new_element.find('.initial').remove();
    $('#id_' + type + '-TOTAL_FORMS').val(parseInt(total)+1);
    $(selector).after(new_element);
  }

  m.poll = {
    init: function(add_more_selector, last_form_selector) {
      if(typeof(add_more_selector) === 'undefined') add_more_selector = '#add_more_poll_option';
      if(typeof(last_form_selector) === 'undefined') last_form_selector = '#poll_formset div.poll-option-form:last';

      $(add_more_selector).click(function(ev) {
        ev.preventDefault();
        cloneFormset(last_form_selector, 'poll');
      });
    }
  };

  m.attachment = {
    init: function(add_more_selector, last_form_selector) {
      if(typeof(add_more_selector) === 'undefined') add_more_selector = '#add_more_attachment';
      if(typeof(last_form_selector) === 'undefined') last_form_selector = '#attachment_formset div.attachment-form:last';

      $(add_more_selector).click(function(ev) {
        ev.preventDefault();
        cloneFormset(last_form_selector, 'attachment');
      });
    }
  };

  m.init = function() {
  };

  return m;
})(machina || {}, jQuery);
