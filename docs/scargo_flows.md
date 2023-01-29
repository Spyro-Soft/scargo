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
