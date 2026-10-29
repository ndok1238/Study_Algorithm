# Git / GitHub 상세 가이드

> 전제: commit / push / pull 은 이미 사용 중. 이 컴퓨터에 로그인된 GitHub 계정과 **다른 계정**으로 사용.

---

## 0. 다른 계정으로 사용하기 (가장 먼저)

문제: Windows는 **자격 증명 관리자(Credential Manager)** 에 기존 계정의 GitHub 로그인을 저장해 둔다.
HTTPS로 push하면 기존 계정으로 시도하다 `403 Permission denied` 가 난다.

### 방법 A. SSH 키 + Host 별칭 (권장)

1. 새 계정 전용 키 생성
   ```bash
   ssh-keygen -t ed25519 -C "새계정@이메일" -f ~/.ssh/id_ed25519_study
   ```
2. 공개키(`~/.ssh/id_ed25519_study.pub`) 내용을 새 계정 GitHub → Settings → SSH and GPG keys → New SSH key 에 등록
3. `~/.ssh/config` 에 별칭 추가
   ```
   Host github-study
       HostName github.com
       User git
       IdentityFile ~/.ssh/id_ed25519_study
       IdentitiesOnly yes
   ```
4. 연결 테스트
   ```bash
   ssh -T git@github-study     # "Hi 새계정! ..." 가 나오면 성공
   ```
5. 저장소 주소는 `github.com` 대신 별칭 사용
   ```bash
   git remote add origin git@github-study:새계정/저장소.git
   git clone git@github-study:새계정/저장소.git
   ```

### 방법 B. HTTPS + 토큰 (간단하지만 기존 계정과 충돌 가능)

- GitHub → Settings → Developer settings → Personal access tokens 에서 토큰 발급
- 자격 증명 관리자에서 `git:https://github.com` 항목을 삭제하거나, 아래 설정으로 경로별 구분
  ```bash
  git config --global credential.useHttpPath true
  ```
- push 시 계정 이름 + 토큰(비밀번호 칸)을 입력

### 방법 C. GitHub CLI 다중 계정
```bash
gh auth login        # 새 계정 추가 로그인
gh auth switch       # 계정 전환
gh auth status
```

### 커밋 작성자(author) 분리 — 필수
계정이 다르면 `user.name` / `user.email` 도 달라야 커밋이 새 계정에 연결된다.

```bash
# 이 저장소에만 적용 (--global 쓰지 않기)
git config user.name  "새계정이름"
git config user.email "새계정@이메일(또는 noreply 주소)"
git config --list --show-origin | findstr user      # 확인
```

폴더 단위로 자동 적용하려면 (`~/.gitconfig`):
```
[includeIf "gitdir:D:/Work/Work/ClaudeWorkspace/Study/"]
    path = ~/.gitconfig-study
```
`~/.gitconfig-study` 에 `[user] name=..., email=...` 작성.

> 이메일 비공개를 원하면 GitHub → Settings → Emails 의 `ID+이름@users.noreply.github.com` 사용.

---

## 1. Git의 구조 이해

```
Working Directory  --git add-->  Staging Area  --git commit-->  Local Repo  --git push-->  Remote(GitHub)
   (작업 폴더)                    (index)                        (.git)                      (origin)
```

- **commit**: 스냅샷 + 메시지 + 부모 커밋 링크. 해시(SHA)로 식별
- **branch**: 특정 커밋을 가리키는 움직이는 포인터
- **HEAD**: 지금 내가 보고 있는 커밋/브랜치
- **origin**: 원격 저장소의 기본 별칭
- `pull` = `fetch`(받아오기) + `merge`(합치기)

---

## 2. 기본 명령어

```bash
git init                        # 새 저장소
git clone <url>                 # 복제
git status                      # 상태 (자주 확인)
git add <파일> / git add .      # 스테이징
git add -p                      # 변경 조각 단위로 선택 스테이징
git commit -m "메시지"
git commit --amend              # 직전 커밋 수정 (push 전에만)
git log --oneline --graph --all # 그래프로 이력 보기
git diff                        # 작업 폴더 vs 스테이징
git diff --staged               # 스테이징 vs 마지막 커밋
git show <커밋>                 # 커밋 내용
```

### .gitignore
```
node_modules/
.env
*.log
.vscode/
```
- 이미 추적 중인 파일 제외: `git rm --cached <파일>`
- **비밀키/토큰/.env 는 절대 커밋 금지** (한 번 올라가면 이력에 남는다)

### 커밋 메시지 규칙 (Conventional Commits)
```
feat: 로그인 API 추가
fix: 토큰 만료 시 null 반환 버그 수정
docs: README 설치 방법 보강
refactor / test / chore / style
```
한 커밋 = 한 가지 목적. 제목 50자 내외, 명령형.

---

## 3. 브랜치

```bash
git branch                      # 목록
git switch -c feature/login     # 생성 + 이동
git switch main                 # 이동
git branch -d feature/login     # 삭제(병합된 것)
git branch -D feature/login     # 강제 삭제
git branch -m 새이름            # 이름 변경
```

### 병합 방법 3가지

| 방식 | 명령 | 결과 |
|---|---|---|
| Merge | `git merge feature` | 병합 커밋 생성, 이력 보존 |
| Fast-forward | (분기 없을 때 merge) | 포인터만 이동, 직선 이력 |
| Rebase | `git rebase main` | 내 커밋을 main 끝에 다시 쌓아 직선 이력 |

- **rebase 황금률**: 이미 push해서 남이 가져간 커밋은 rebase 하지 않는다
- Squash merge: PR의 여러 커밋을 하나로 합쳐 main에 반영 (GitHub PR 버튼에서 선택)

### 충돌(conflict) 해결
```
<<<<<<< HEAD
내 변경
=======
상대 변경
>>>>>>> feature
```
1. 파일을 열어 마커 제거하고 최종 내용으로 수정
2. `git add <파일>`
3. `git commit` (rebase 중이면 `git rebase --continue`)
4. 포기하려면 `git merge --abort` / `git rebase --abort`

---

## 4. 되돌리기 (가장 중요한 영역)

| 상황 | 명령 |
|---|---|
| 작업 폴더 변경 버리기 | `git restore <파일>` |
| 스테이징 취소 | `git restore --staged <파일>` |
| 직전 커밋 메시지/내용 수정 | `git commit --amend` |
| 커밋 취소, 변경은 스테이징에 유지 | `git reset --soft HEAD~1` |
| 커밋 취소, 변경은 작업 폴더에 유지 | `git reset --mixed HEAD~1` (기본) |
| 커밋 + 변경 모두 삭제 (위험) | `git reset --hard HEAD~1` |
| **이미 push한** 커밋 취소 | `git revert <커밋>` (취소하는 새 커밋 생성) |
| 실수로 날린 커밋 복구 | `git reflog` → `git reset --hard <해시>` |

- 원칙: **push 전 = reset / amend, push 후 = revert**
- `git push --force` 는 공유 브랜치에서 금지. 꼭 필요하면 `--force-with-lease`

### stash (작업 임시 보관)
```bash
git stash push -m "작업중"
git stash list
git stash pop            # 꺼내서 적용 + 삭제
git stash apply          # 적용만
```

### 특정 커밋만 가져오기
```bash
git cherry-pick <커밋해시>
```

---

## 5. 원격 저장소

```bash
git remote -v
git remote add origin <url>
git remote set-url origin <새url>       # 주소 변경 (계정 별칭 바꿀 때)
git push -u origin main                 # 최초 push, 이후 git push 만
git fetch                               # 받아오기만 (안전)
git pull --rebase                       # 불필요한 병합 커밋 방지
git push origin --delete <브랜치>       # 원격 브랜치 삭제
git fetch --prune                       # 삭제된 원격 브랜치 정리
```

push가 거절될 때(`rejected, non-fast-forward`): 원격에 내가 없는 커밋이 있다 → `git pull --rebase` 후 다시 push.

---

## 6. GitHub 협업 흐름

### 기본 흐름 (GitHub Flow)
```
main 최신화 → feature 브랜치 생성 → 작업/커밋 → push → Pull Request → 리뷰 → Merge → 브랜치 삭제
```
```bash
git switch main && git pull
git switch -c feature/xxx
# ... 작업, 커밋 ...
git push -u origin feature/xxx
# GitHub에서 PR 생성  (또는: gh pr create)
```

### Pull Request 잘 쓰기
- 제목: 무엇을 했는지 한 줄
- 본문: 변경 이유, 주요 변경점, 테스트 방법, 관련 이슈 (`Closes #12` 쓰면 병합 시 이슈 자동 종료)
- 작게 자주 올리기 (변경 300줄 이하가 이상적)
- 혼자 쓰는 저장소여도 PR로 연습하면 좋다

### Fork 흐름 (남의 저장소에 기여)
```bash
# GitHub에서 Fork → 내 계정으로 clone
git remote add upstream <원본url>
git fetch upstream
git switch main && git merge upstream/main    # 원본 최신화
```

### GitHub 기능 정리
- **Issues**: 할 일/버그 추적, 라벨·마일스톤·담당자
- **Projects**: 칸반 보드
- **Actions**: CI/CD 자동화 (`.github/workflows/*.yml`)
- **Branch protection**: Settings → Branches 에서 main 직접 push 금지, PR 리뷰 필수, CI 통과 필수
- **Releases / Tags**: 버전 배포 (`git tag v1.0.0 && git push --tags`)
- **README.md, LICENSE, CONTRIBUTING.md**: 저장소 얼굴

### GitHub CLI (gh)
```bash
gh repo create study --private --source=. --push
gh pr create --fill
gh pr list / gh pr checkout 12 / gh pr merge
gh issue create / gh issue list
```

---

## 7. 이 Study 폴더 시작하기 (실습 1)

```bash
cd D:/Work/Work/ClaudeWorkspace/Study
git init -b main
git config user.name  "새계정이름"
git config user.email "새계정@이메일"
echo "# Study" > README.md
git add . && git commit -m "chore: init study repo"

# GitHub(새 계정)에서 빈 저장소 'study' 생성 후
git remote add origin git@github-study:새계정/study.git
git push -u origin main
```

---

## 8. 연습 과제

1. 브랜치 `feature/a`, `feature/b` 에서 **같은 줄**을 수정 → merge 해서 충돌을 직접 만들고 해결
2. 커밋 3개 만들고 `git reset --soft HEAD~3` 후 하나로 다시 커밋
3. `git reset --hard` 로 커밋을 날린 뒤 `git reflog` 로 복구
4. 커밋 5개짜리 브랜치를 `git rebase -i HEAD~5` 로 정리(squash, reword)
5. 브랜치 → PR → squash merge → 브랜치 삭제까지 한 사이클 수행
6. `.env` 를 실수로 커밋했다고 가정하고 이력에서 제거하는 방법 조사 (`git filter-repo`) 및 키 폐기가 먼저인 이유 정리
7. Actions 로 push 시 `echo hello` 하는 워크플로우 작성

## 9. 자주 겪는 오류

| 오류 | 원인 / 해결 |
|---|---|
| `403 Permission denied to 다른계정` | 자격 증명 캐시 문제 → SSH 별칭 사용 또는 자격 증명 관리자 정리 |
| `Permission denied (publickey)` | 키 미등록 또는 `ssh -T git@github-study` 로 점검 |
| 커밋이 내 계정 프로필에 안 보임 | `user.email` 이 GitHub 계정 이메일과 불일치 |
| `rejected ... non-fast-forward` | `git pull --rebase` 후 재push |
| `detached HEAD` | 커밋 체크아웃 상태 → `git switch -c 새브랜치` 로 보존 |
| CRLF/LF 경고 | `git config core.autocrlf true` (Windows) |

## 10. 추천 학습 자료
- Pro Git (한국어 무료): https://git-scm.com/book/ko/v2
- 시각화 연습: https://learngitbranching.js.org
- GitHub Skills: https://skills.github.com
