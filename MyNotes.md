How to perform the Zooming function

since canvas frame in inside frameTwo, and frameTwo is black in color
we will store the  width and height of the canvas frame in a variable 



<!-- ! when the user will decrement the value of the zoom let suppose 100 to 99% -->

<!-- ? then the width and height will be reinitialized with recalculate value -->

<!-- How to calculate the value -->

let's suppose the width is 1000px, user decrements from 100 to 99% then the latest width will be 99% of the old width which is 1000
<!-- Thereforre new width = 900px -->

<!-- ! Same thing will happen with height  -->

newWidth = oldWidth x scaleValue/100

