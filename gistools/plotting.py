import matplotlib.pyplot as plt
import seaborn as sns

def barplot(
	data, x, y, 
	xlabel=None, xaxis_visible=True, xorient=0, 
	ylabel=None, yaxis_visible=True, ylabel_offset=1.02, yscale='linear', ylimit=None, 
	title=None, grid=True, style='ggplot', axes_style='whitegrid', palette=['DodgerBlue'], figsize=(16,8), fontsize=12):

	plt.Normalize(data[y].values.min(), data[y].values.max())

	plt.style.use(style)

	plt.figure(figsize=figsize)
	plt.title(title)
	plt.grid(grid)

	if axes_style is not None:
		sns.set_style(axes_style)  

	if xlabel is None:
		xlabel = x
	if ylabel is None:
		ylabel = y

	ax1 = sns.barplot(x=x, y=y, data=data, palette=palette)
	ax1.set(xlabel=xlabel, ylabel=ylabel)
	ax1.set_yscale(yscale)

	x_axis = ax1.axes.get_xaxis()
	x_axis.label.set_visible(xaxis_visible)
	if xaxis_visible:
		if xorient > 0:
			for item in ax1.get_xticklabels():
				item.set_rotation(xorient)

	if ylabel_offset is not None:
		blabels = [label for label in list(data[y])]
		for i, pb in enumerate(ax1.patches):
			_x = pb.get_x() + pb.get_width () / 2
			_y = pb.get_y() + pb.get_height() * ylabel_offset
			value = blabels[i]
			ax1.text(_x, _y, value, ha="center") 
	
	if ylimit is not None:
		ax2 = sns.lineplot(x=x, y=ylimit, data=data)

	plt.gcf()

	return plt

#EOF