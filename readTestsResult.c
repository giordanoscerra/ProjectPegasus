#include <stdio.h>

//define coupple
typedef struct {
    int testNumber;
    int nSteps;
    float reward;
} couple;


//define read line
void readLineFromFile(FILE *fp, couple *c) {
    fscanf(fp, "%d: rewards:<%f> steps:<%d>", &(*c).testNumber, &(*c).reward, &(*c).nSteps);
}

int main() {
    FILE *fp;
    char buff[255];

    fp = fopen("./stats2.txt", "r");
    int tot_episodes = 200;
    int tot_steps = 0;
    float tot_reward = 0;
    int steps_on_success = 0;
    int tot_success = 0;
    for (int i = 0; i < tot_episodes; i++) {
        couple c;
        c.testNumber = i;
        readLineFromFile(fp, &c);
        //printf("Test number: %d, nSteps: %d, reward: %.0f\n", c.testNumber, c.nSteps, c.reward);
        tot_steps += c.nSteps;
        tot_reward += c.reward;
        if (c.reward > 5){
            steps_on_success += c.nSteps;
            tot_success++;
        }
    }
    printf("Average steps: %.1f, winning: %.2f\n", tot_steps / (float) tot_episodes, ((float) tot_reward / tot_episodes) / 1000.0);
    printf("Average steps on success: %.1f\n", steps_on_success / (float) tot_success);
    printf("Average step on failure: %.1f\n", (tot_steps - steps_on_success) /(float) (tot_episodes - tot_success));
    fclose(fp);
    return 0;
}