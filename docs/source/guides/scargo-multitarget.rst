.. _scargo_multitarget:

Multitarget support in scargo
=============================

Creating a project
------------------
With scargo you are able to create multitarget project by specifying --target option multiple times.
For [atsam, esp32, stm32] targets if --chip option is not specified, default chip will be used. It's
also possible to specify --chip option instead (or with) --target option to specify the chip for each target.

Let's say we want to create a project for atsam and stm32 targets. We can do it by running the following command:

::

    scargo new --target atsam --target stm32 [project_name]

This will create a project with two targets: atsam and stm32, with default chips `ATSAMD10D14AM` and `STM32F100RBT6` respectively.
If instead we would like to specify different chips for each target we can do it by running the following command:

::

        scargo new --chip atsamd10d14am --chip STM32F100RBT6 [project_name]

Target is automatically deduced from chip labels. This means that in this case it's optional to specify --target for already specified chips.
So, the following commands will create thes same project as above:

::

        scargo new --target atsam --chip atsamd10d14am --chip STM32F100RBT6 [project_name]
        scargo new --target stm32 --chip atsamd10d14am --chip STM32F100RBT6 [project_name]
        scargo new --target atsam --target stm32 --chip atsamd10d14am --chip STM32F100RBT6 [project_name]

**First target that is specified will be used as default target.**
If at some point you would like to add/remove a target or change chip for some target, you can do it by modifying `scargo.toml` file.
If you want to change default target, you can do it by modifying order in `scargo.toml` file.
e.g.

::

    target = ["stm32", "atsam"] # default target is stm32
    target = ["x86", "atsam", "stm32"] # default target is x86


Building a project
------------------
To build a project you can run the following command:

::

    scargo build --profile --Release

In this case, since the target is not specified, default target will be used.
If you want to build a project for a specific target, you can do it by specifying --target option:

::

    scargo build --target atsam --profile --Release

Flashing and debugging a project
--------------------------------
As with building the project, if --target option is not specified, default target will be used.
To flash a target you can run the following command:

::

    scargo flash --target [TARGET]


To debug a project you can run the following command:

::

    scargo debug --target [TARGET]

Publishing a project
--------------------

Currently, publishing a multitarget project is limited. When you run scargo publish,
only package for the default target will be published.