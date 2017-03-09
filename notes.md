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
```bash
make DESTDIR=/opt/android/ndk/platforms/android-23/arch-arm/ install
```

通过`cat /system/build.prop | grep product`来获得系统芯片信息。

