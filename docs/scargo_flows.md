# Scargo flows

## New Project x86 dev flow

```console
scargo -h
scargo new -h
scargo new my_project --target x86
cd my_project
git status
git add .
git commit -m 'Initial commit'
scargo docker run
scargo build
scargo check
scargo test
scargo run
exit
```

## New Project esp32 dev flow

```console
scargo -h
scargo new -h
scargo new my_project_esp32 --target esp32
cd my_project_esp32
git add .
git commit -m 'Initial commit'
scargo docker run
idf.py menuconfig
scargo build
scargo gen --fs
scargo check
scargo test
scargo flash -h
scargo flash
scargo flash --fs
idf.py -B build/Debug monitor
ctrl+]
exit
```


## New Project stm32 dev flow

```console
scargo -h
scargo new -h
scargo new my_project_stm32 --target stm32
cd my_project_stm32
git add .
git commit -m 'Initial commit'
scargo docker run
scargo build
scargo check
scargo test
#scargo flash
exit
```

## Clean and build x86

```console
scargo docker run
ls ./build
scargo clean
ls ./build
scargo build --profile Debug
scargo build --profile Release
ls ./build
./build/Release/bin/my_project
./build/Debug/bin/my_project
exit
```

## Check and fix x86

```console
scargo docker run
vi src/my_project.cpp
* make some format issues
wq!
scargo check
scargo fix
scargo check
exit
```

## Change scargo.toml and update

```console
vi CMakeLists.txt
vi scargo.toml
* make some config update
wq!
scargo update
vi CMakeLists.txt
q
exit
```

## Debug existing

```console
ls
scargo docker run
scargo debug
tui enable
b main()
r
n
n
exit
```
