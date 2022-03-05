#include <iostream>

int n;
int map[15][15], total = 0;
int direction[8][2] = {
    { -1, 0 }, { 1, 0 }, { 0, -1 }, { 0, 1 }, { -1, -1 }, { -1, 1 }, { 1, -1 }, { 1, 1 }
};

bool visited[15][15];

bool checkIndex(int x, int y) { return x >= 0 && x < n && y >= 0 && y < n; }

void search(int x, int y) {
    if (x == 0 && y == n - 1) {
        total += 1;
        return;
    }

    for (int i = 0; i < 8; ++i) {
        int next_x = x + direction[i][0];
        int next_y = y + direction[i][1];
        if (checkIndex(next_x, next_y) && !visited[next_x][next_y] && map[next_x][next_y] != 1) {
            visited[x][y] = true;

            search(next_x, next_y);

            visited[x][y] = false;
        }
        continue;
    }
}

int main() {
    /*std::fstream cin("maze.in", std::ios::in);
          std::fstream cout("maze.out", std::ios::out | std::ios::trunc);*/

    std::cin >> n;

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            std::cin >> map[i][j];
        }
    }

    search(0, 0);

    std::cout << total;

    /*cin.close();
      cout.close();*/

    return 0;
}