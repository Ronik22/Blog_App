var file = document.getElementById('img');

file.onchange = function(e) {
  var ext = this.value.match(/\.([^\.]+)$/)[1];
  switch (ext) {
    case 'jpg':
    case 'jpeg':
    case 'bmp':
    case 'png':
        this.form.submit();
        break;
    default:
      alert('Only JPG, PNG and BMP is allowed');
      this.value = '';
  }
};