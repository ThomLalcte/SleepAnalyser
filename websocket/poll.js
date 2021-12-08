function myFunction() {
    document.getElementById("demo").innerHTML = "Paragraph changed.";
  }

function drawCanvas() {
    var c = document.getElementById("myCanvas");
    var ctx = c.getContext("2d");
    ctx.moveTo(0,0);
    ctx.lineTo(200,100);
    ctx.stroke();
}