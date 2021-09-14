##############################
# 이 위는 일타싸피와 통신하여 데이터를 주고 받기 위해 작성된 부분이므로 수정하면 안됩니다.
#
# 모든 수신값은 gameData에 들어갑니다.
#   - gameData.order: 1인 경우 선공, 2인 경우 후공을 의미
#   - gameData.balls[][]: 일타싸피 정보를 수신해서 각 공의 좌표를 배열로 저장
#     예) gameData.balls[0][0]: 흰 공의 X좌표
#         gameData.balls[0][1]: 흰 공의 Y좌표
#         gameData.balls[1][0]: 1번 공의 X좌표
#         gameData.balls[4][0]: 4번 공의 X좌표
#         gameData.balls[5][0]: 마지막 번호(8번) 공의 X좌표

# 여기서부터 코드를 작성하세요.
# 아래에 있는 것은 샘플로 작성된 코드이므로 자유롭게 변경할 수 있습니다.

# Vector 구현
class Vector:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f'{self.x:.10f}, {self.y:.10f}'

    @property
    def _comp(self):
        return (self.x, self.y)

    def __add__(self, other):
        return Vector(*(i + j for i, j in zip(self._comp, other._comp)))

    @property
    def norm(self):
        return sum(i * i for i in self._comp) ** (1 / 2)

    def dot(self, other):
        return sum(i * j for i, j in zip(self._comp, other._comp))

    def cross(self, other):
        return (self.x * other.y - self.y * other.x)

    def __neg__(self):
        return Vector(*(-i for i in self._comp))

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.cross(other)
        return Vector(*(other * i for i in self._comp))

    def __rmul__(self, other):
        if isinstance(other, Vector):
            return self.cross(other)
        else:
            return self.__mul__(other)

    def __truediv__(self, other):
        return Vector(*(i / other for i in self._comp))


# x 부터 y까지 가는 경로 계산하는 함수
def path_find(x: Vector, y: Vector):
    # x -> y로 가능 1쿠션 구석 쿠션 고려한 모든 가능한 길 반환
    # 반환 형  [path.norm,sv,fv] 출발 단위백터와 도착 단위백터, path.norm은 총 길이
    def makemirrorset(y):
        # 목적지의 미러셋을 만듬
        ret = []
        for xm in [-1, 0, W]:
            for ym in [-1, 0, H]:
                new = copy(y)
                if xm != -1:
                    new.x = 2 * xm - new.x
                if ym != -1:
                    new.y = 2 * ym - new.y
                ret.append(new)
        return ret

    def path_check(start, end):
        # todo
        # 경로중에 공,홀,등등이 있으면 제외
        # path divide
        paths = [[start, end]]
        while not (0 <= paths[-1][-1].x <= W and 0 <= paths[-1][-1].y <= H):
            ndt_split = paths.pop()
            s = ndt_split[0]
            e = ndt_split[1]
            checkvec = e - s

            if e.y > H:
                a = H - s.y
                b = e.y - H
                new_s_x = a * checkvec.x / (a + b) + s.x
                new_s_y = H
                new_s = Vector(new_s_x, new_s_y)
                new_e = copy(e)
                new_e.y = 2 * H - new_e.y
                paths.append([s, new_s])
                paths.append([new_s, new_e])
            elif e.y < 0:
                a = -s.y
                b = e.y
                new_s_x = a * checkvec.x / (a + b) + s.x
                new_s_y = 0
                new_s = Vector(new_s_x, new_s_y)
                new_e = copy(e)
                new_e.y = -new_e.y
                paths.append([s, new_s])
                paths.append([new_s, new_e])

            if e.x > W:
                a = W - s.x
                b = e.x - W
                new_s_y = a * checkvec.y / (a + b) + s.y
                new_s_x = W
                new_s = Vector(new_s_x, new_s_y)
                new_e = copy(e)
                new_e.x = 2 * W - new_e.x
                paths.append([s, new_s])
                paths.append([new_s, new_e])
            elif e.x < 0:
                a = -s.x
                b = e.x
                new_s_y = a * checkvec.y / (a + b) + s.y
                new_s_x = 0
                new_s = Vector(new_s_x, new_s_y)
                new_e = copy(e)
                new_e.x = -new_e.x
                paths.append([s, new_s])
                paths.append([new_s, new_e])

        cnt = 0
        # 거리 -> uxr/u.norm = |u||r|sin()/|u|, if cos < 0 path
        # print(start,end)
        # print(paths)
        for path in paths:
            # path = [start,end]
            tstart = path[0]
            tend = path[1]
            checkvec = tend - tstart
            if checkvec.norm == 0:
                return False
            checkvec = checkvec / checkvec.norm
            for ball in objball + enemyball + [myball] + Myholes:
                checkball = ball - tstart
                if checkvec.dot(checkball) < 0:
                    continue
                if abs(checkvec.cross(checkball)) < 1.5 * Ball_r:
                    cnt += 1
        # print(start,end,cnt)
        if cnt > 2:
            return False
        return True

    def path_split(path: Vector, start, end):
        # 테이블 벗어나는 패스를 쪼개어줌 x
        # 시작 백터, 끝백터, 길이만 알면 될 듯? check는 했으니
        sv = copy(path) / path.norm
        fv = copy(path) / path.norm
        if end.y < 0 or end.y > H:
            fv.y = -fv.y
        if end.x < 0 or end.x > W:
            fv.x = -fv.x

        return [path.norm, sv, fv]

    ally = makemirrorset(y)
    paths = list(map(lambda k: k - x, ally))
    # print(paths)
    ret = []
    for idx, path in enumerate(paths):
        if path_check(x, ally[idx]):
            ret.append(path_split(path, x, ally[idx]))

    return ret


def find_bestway(obj):
    cand_path = []
    for hole in Myholes:
        # obj이 hole에 가는 방법
        # 쿠션 고려, [길이,시작백터,끝백터]
        objtoholes = path_find(obj, hole)
        best_hole = []
        if not objtoholes:
            print('not any objtohole pass')
            continue
        for objtohole in objtoholes:
            objtohole_nv = objtohole[1]
            que = obj - Ball_R * objtohole[1]
            # 수구 to que점을 가는 길 계산
            quetoobjs = path_find(myball, que)
            if not quetoobjs:
                print('not any quetoobj pass')
                continue
            for quetoobj in quetoobjs:
                quetoobj_nv = quetoobj[2]
                # 두 백터의 각도 계산 (단위백터끼리의 내적)
                # 영보다 작거나 음수면 안하고 진행
                collcos = objtohole_nv.dot(quetoobj_nv)
                if collcos <= 0:
                    continue
                mue = 8
                v1h = (60 + 2 * mue * objtohole[0])
                v01 = (v1h + 2 * mue * quetoobj[0]) ** (1 / 2) + 3
                inferF = quetoobj[1] * v01
                inferF = inferF / (collcos ** (1 / 2))
                weight = 100
                c1 = 2
                c2 = 0.01
                weight *= c1 * math.log2((objtohole_nv.dot(quetoobj_nv) * 1000))
                weight /= c2 * (inferF.norm ** (1.4))
                print('1', c1 * math.log2((objtohole_nv.dot(quetoobj_nv) * 100)))
                print('2', c2 * (inferF.norm ** (1.4)))
                best_hole.append([weight, inferF.norm, inferF])
                # cand_path.append([int(objtohole_nv.dot(quetoobj_nv) * 10), inferF.norm, inferF])

        best_hole.sort(key=lambda x: (-x[0], x[1]))
        if best_hole:
            cand_path.append(best_hole[0])
    return cand_path


Ball_r = 5.73 / 2
Ball_R = 5.73
W = 254
H = 127
# 일부러 홀의 위치를 보이기보다 약간 안쪽으로 잡아당겨줌
# HOLES = [[0+Ball_r/4, 0+Ball_r/4], [127, 0+Ball_r/3], [254-Ball_r/4, 0+Ball_r/4], [0+Ball_r/4, 127-Ball_r/4], [127, 127-Ball_r/3], [254-Ball_r/4, 127-Ball_r/4]]

const = 0.15
k = Ball_r * const
# k = 0
HOLES = [[0 + k, 0 + k], [127, 0 + k / 2], [254 - k, 0 + k], [0 + k, 127 - k], [127, 127 - k / 2], [254 - k, 127 - k]]
Myholes = []
for hole in HOLES:
    Myholes.append(Vector(*hole))
    # 홀 위치를 더 추가해서 정확도를 올리려했으나 실패?
    # for _ in range(20):
    #     seta = _*2*math.pi/20
    #     addvector = Vector(math.cos(seta),math.sin(seta))*Ball_r/20
    #     Myholes.append(Vector(*hole) + addvector)

# 내공
myball = Vector(*gameData.balls[0])
# 목적구
objball = []
# 상대구
enemyball = []

print(myball)
# 공을 정리함 -> 목적구 2개가 안넣어졌으면 8볼은 상대목적구로 봄
flag1 = False
flag2 = False
if gameData.order == 1:
    for idx, ball in enumerate(gameData.balls[1:]):
        # 목적구 2개가 다 끝났으면 True
        if ball == [-1.0, -1.0]:
            if idx == 0:
                flag1 = True
            if idx == 2:
                flag2 = True
            continue
        else:
            if idx == 0 or idx == 2:
                objball.append(Vector(*ball))
            elif idx == 1 or idx == 3:
                enemyball.append(Vector(*ball))
            elif idx == 4:
                if flag1 and flag2:
                    objball.append(Vector(*ball))
                else:
                    enemyball.append(Vector(*ball))
        # print(flag1,flag2)
else:
    for idx, ball in enumerate(gameData.balls[1:]):
        # 목적구 2개가 다 끝났으면 True
        if ball == [-1.0, -1.0]:
            if idx == 1:
                flag1 = True
            if idx == 3:
                flag2 = True
            continue
        else:
            if idx == 1 or idx == 3:
                objball.append(Vector(*ball))
            elif idx == 0 or idx == 2:
                enemyball.append(Vector(*ball))
            elif idx == 4:
                if flag1 and flag2:
                    objball.append(Vector(*ball))
                else:
                    enemyball.append(Vector(*ball))
        # print(flag1,flag2)

# print(myball)
# print(objball)
# print(enemyball)

Pathlist = []
# 내 목적구에 대해서만
for obj in objball:
    cand_path = find_bestway(obj)
    if cand_path:
        Pathlist.extend(cand_path)


# 백터로 계산한 힘을 힘과 각도로 변환해줌
def Fchange(Pathnorm, Path: Vector):
    forcal = Path / (Pathnorm)
    if forcal.x >= 0 and forcal.y >= 0:
        seta = math.asin(Vector(1, 0).cross(forcal))

    elif forcal.x <= 0 and forcal.y >= 0:
        seta = math.asin(Vector(0, 1).cross(forcal)) + math.pi / 2

    elif forcal.x <= 0 and forcal.y <= 0:
        seta = math.asin(Vector(-1, 0).cross(forcal)) + math.pi

    else:
        seta = math.asin(Vector(0, -1).cross(forcal)) + 3 * math.pi / 2

    weight1 = 0.6
    weight2 = 15

    print('weight1', (Pathnorm * weight1) / (Pathnorm * weight1 + weight2), 'weight2',
          (weight2) / (Pathnorm * weight1 + weight2))
    F = Pathnorm * weight1 + weight2
    degree = seta * 180 / math.pi
    degree = ((90 - degree) + 360) % 360
    if len(objball) == 1:
        F *= 1.01
    if F > 100:
        F = 100
    return F, degree


# 가장 일직선으로 만나는 것 + 다음으로 힘의 필요가 가장 작은 것을 쓰자
Pathlist.sort(key=lambda x: (-x[0], x[1]))
print(Pathlist)
# 만약에 하나도 없으면
if not Pathlist:
    tmp_list = []
    for obj in objball:
        tmp = path_find(myball, obj)
        if not tmp:
            continue
        tmp.x *= 1.001
        tmp.y *= 1.001
        tmp_list.append([tmp.norm, tmp])

    if not tmp_list:
        for obj in objball:
            temp = obj - myball
            temp = temp + Vector(0, temp.y)
            power, angle = Fchange([temp.norm, temp])
            break
    else:
        tmp_list.sort()
        power, angle = Fchange(*tmp_list[0])
        power = 100


else:
    # Pathlist = [[가중치1:각도, 가중치2:Norm, F백터]  ]
    power, angle = Fchange(*Pathlist[0][1:])

# conn.send(angle, power)
print(f'Power: {power}, Angle: {angle}')