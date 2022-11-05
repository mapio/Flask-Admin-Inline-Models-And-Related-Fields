(function() {
  var $parent = $('#parent');
  var $related_child = $('#related_child');
  $parent.change(function() {
    var $parent_id = $parent.select2('data').id;
    $.ajax({
      url: '/related/ajax/lookup/',
      data: {
        name: 'related_child',
        query: $parent_id
      }, 
      success: function(data) {
        $related_child.empty();
        $related_child.append(
          new Option(' ', '__None', false, false)
        );
        data.forEach(function(elem) {
          $related_child.append(
            new Option(elem[1], elem[0], false, false)
          );
        });
        $related_child.trigger('change'); 
      }
    });
  });
})();