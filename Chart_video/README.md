# 利用matplotlib绘制竞赛条形动态图

### 数据来源：[1900-2018城市人口数量](https://gist.githubusercontent.com/johnburnmurdoch/4199dbe55095c3e13de8d5b2e5e5307a/raw/fa018b25c24b7b5f47fd0568937ff6c04e384786/city_populations)

#### 函数功能划分:dango:

* 数据获取，颜色代码生成，地区:颜色 字典键值对生成:collision:
* 条形图基本功能（数据，标签）生成；
* 图标细节格式修饰:deciduous_tree:：
  * Text，字体大小，颜色，走向；
  * Format，逗号分割的值和坐标轴；
  * Axis，位置方向，上方，颜色，子标题；
  * Grid，在图表后面加线；
  * plt.box(False)，去除整体方框；
  * 增加标题，credit;

---

* 利用**matplotlib.animation.FuncAnimation()**进行动画生成；

#### 个人建议：代码结合博客食用效果更佳，博客地址：https://blog.csdn.net/weixin_42512684

#### 鉴于个人水平有限，如有问题可以在公众号（Z先生点记）后台留言：

**公众号二维码地址：**
<br>
![Snipaste_2020-02-08_16-08-20.jpg](http://ww1.sinaimg.cn/large/007wRTdIly1gbp24g2fhlj30kc07a0th.jpg)
