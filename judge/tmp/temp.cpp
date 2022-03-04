#include <iostream>
#include <algorithm>
#include <cstring>
#include <queue>
using namespace std;

struct node {
    int x, y, z, step;
};

int d[4][2] = { 0, 1, 1, 0, 0, -1, -1, 0 };
int vis[11][11][3];
char s[11][11][3];
int sx, sy, sz, ex, ey, ez;
int flag;
int m, n, tt, t;

void bfs(int x, int y, int z, int step) {
    memset(vis, 0, sizeof vis);

    node e1{ x, y, z, 0 }, e2;
    e1.x = x;
    e1.y = y;
    e1.z = z;
    e1.step = 0;

    vis[x][y][z] = 1;
    queue<node> que;
    que.push(e1);

    while (!que.empty()) {
        e1 = que.front();
        que.pop();

        if (s[e1.x][e1.y][e1.z] == 'P') {
            if (e1.step <= t) {
                flag = 1;
            }
            break;
        }

        for (int i = 0; i < 4; i++) {
            e2.x = e1.x + d[i][0];
            e2.y = e1.y + d[i][1];
            e2.z = e1.z;

            if (e2.x >= 0 && e2.x < n && e2.y >= 0 && e2.y < m && !vis[e2.x][e2.y][e2.z] &&
                s[e2.x][e2.y][e2.z] != '*') {
                if (s[e2.x][e2.y][e2.z] != '#') {
                    vis[e2.x][e2.y][e2.z] = 1;
                    e2.step = e1.step + 1;
                    que.push(e2);
                } else {
                    vis[e2.x][e2.y][e2.z] = 1;
                    if (e1.z == 0) {
                        e2.z = 1;
                        if (s[e2.x][e2.y][e2.z] != '*' && s[e2.x][e2.y][e2.z] != '#') {
                            e2.step = e1.step;
                            vis[e2.x][e2.y][e2.z] = 1;
                            que.push(e2);
                        }
                    } else {
                        e2.z = 0;
                        if (s[e2.x][e2.y][e2.z] != '*' && s[e2.x][e2.y][e2.z] != '#') {
                            e2.step = e1.step;
                            vis[e2.x][e2.y][e2.z] = 1;
                            que.push(e2);
                        }
                    }
                }
            }
        }
    }
}

int main() {

    cin >> tt;

    while (tt--) {
        flag = 0;
        cin >> m >> n >> t;

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                cin >> s[i][j][0];
                if (s[i][j][0] == 'S') {
                    sx = i;
                    sy = j;
                    sz = 0;
                }
            }
        }

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                cin >> s[i][j][1];
                if (s[i][j][1] == 'S') {
                    sx = i;
                    sy = j;
                    sz = 1;
                }
            }
        }

        bfs(sx, sy, sz, 1);

        if (flag)
            cout << "YES" << endl;
        else
            cout << "NO" << endl;
    }

    return 0;
}