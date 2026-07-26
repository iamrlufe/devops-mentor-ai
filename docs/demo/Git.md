# Git

Git хранит историю проекта как последовательность коммитов, каждый из которых
ссылается на предыдущий.

## Ежедневный цикл

```bash
git status
git add .
git commit -m "Add feature"
git push
```

## Ветки

```bash
git switch -c feature/my-change
git switch develop
git merge feature/my-change
```

Ветка — это подвижный указатель на коммит, поэтому её создание почти
бесплатно по времени и по месту.

## Практика

`git log --oneline --graph --all` показывает структуру истории целиком.
Перед `git merge` полезно выполнить `git pull`, чтобы влить свежие изменения
и увидеть конфликты до слияния, а не после.
