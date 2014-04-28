mencoder mf://img_dir/*.png -mf type=png:w=600:h=600:fps=8 -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o output.avi
