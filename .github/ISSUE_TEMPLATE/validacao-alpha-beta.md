---
name: Validação da alpha para beta
about: Checklist de validação completa de uma alpha antes do release beta
title: "Validação da alpha v<versão> para beta"
type: Task
projects: ["proracingsimulators/1"]
---

Verificações a fazer antes de promover uma alpha para beta, quando uma mudança grande pede validação completa.

**Alpha validada:** v<versão>-alpha

### Versões de firmware

- [ ] Verificar as versões do prs_sdk_fw de cada firmware. Se alguma firmware estiver usando uma versão desatualizada do sdk, uma nova versão de firmware para a versão mais recente do sdk deve ser gerada.

### MotionPRS (versão sport)

- [ ] Validar atualização de firmware ao abrir o app com dispositivo na firmware antiga
- [ ] Validar conexão do dispositivo na tela de monitoramento
- [ ] Remover e recolocar o usb para verificar se a reconexão automática está funcionando
- [ ] Acessar tela de calibração e realizar calibração do dispositivo
- [ ] Acessar tela de ajustes e realizar alterações sutis de parâmetros para verificar se algum erro ocorre
- [ ] Acessar a tela de testes e realizar movimentos manuais no Motion para verificar seu funcionamento
- [ ] Acessar a tela de monitoramento para verificar se o monitoramento do dispositivo está correto durante o jogo
- [ ] Validar funcionamento do Motion no Iracing
- [ ] Validar funcionamento do Motion no Assetto Corsa
- [ ] Validar funcionamento do Motion no Assetto Corsa Competizione
- [ ] Validar funcionamento do Motion no Automobilista 2

### PedalPRS (versão Sport)

- [ ] Atualizar firmware do pedal caso uma nova firmware esteja disponível
- [ ] Validar conexão do dispositivo na tela de monitoramento
- [ ] Remover e recolocar o usb para verificar se a reconexão automática está funcionando
- [ ] Acessar tela de calibração e realizar calibração do dispositivo
- [ ] Acessar tela de ajustes e realizar alterações sutis de parâmetros para verificar se algum erro ocorre
- [ ] Acessar a tela de shaker e realizar alterações sutis de parâmetros para verificar se algum erro ocorre
- [ ] Acessar a aba de Teste e testar os shakers do pedal
- [ ] Acessar a aba Monitor para verificar se o monitoramento dos pedais estão funcionando durante os jogos
- [ ] Validar funcionamento do shaker dos pedais no Iracing
- [ ] Validar funcionamento do shaker dos pedais no Assetto Corsa
- [ ] Validar funcionamento do shaker dos pedais no Assetto Corsa Competizione
- [ ] Validar funcionamento do shaker dos pedais no Automobilista 2

### Leds e LCD (versão hub gt)

- [ ] Validar conexão do dispositivo na tela de monitoramento
- [ ] Remover e recolocar o usb para verificar se a reconexão automática está funcionando
- [ ] Acionar botões, encoders e borboletas do volante na tela de monitoramento para verificar o funcionamento
- [ ] Na tela de leds realizar ajustes para verificar se as cores dos leds estão alterando corretamente
- [ ] Na tela de ajustes testar a função “Embreagens Interligadas”
- [ ] Com a função “Embreagens Interligadas” ativa ajustar o centro para verificar se há alterações na leitura das embreagens
- [ ] Desativar a função “Embreagens Interligadas” e verificar se a leitura individual das embreagens ocorre corretamente
- [ ] Acionar a função “Calibrar”. Realizar o procedimento de calibração do dispositivo.
- [ ] Na tela de monitoramento validar novamente o acionamento dos botões, encoders e borboletas para garantir que o funcionamento está correto após a calibração
- [ ] Validar funcionamento dos leds de rpm no Iracing
- [ ] Validar funcionamento dos leds de rpm no Assetto Corsa
- [ ] Validar funcionamento dos leds de rpm no Assetto Corsa Competizione
- [ ] Validar funcionamento dos leds de rpm no Automobilista 2

### Base e Direção (versão hub gt)

- [ ] Validar conexão do dispositivo na tela de monitoramento
- [ ] Remover e recolocar o usb para verificar se a reconexão automática está funcionando
- [ ] Na tela de ajustes realizar modificações sutis nos parâmetros para verificar se algum erro ocorre
- [ ] Ajustar ângulo do volante para 270 graus e testar volante até os batentes
- [ ] Ajustar ângulo do volante para 540 graus e testar volante até os batentes
- [ ] Ajustar ângulo do volante para 900 graus e testar volante até os batentes

### Sistema de vibração (novo app do shaker)

- [ ] Validar conexão do dispositivo na tela de monitoramento
- [ ] Remover e recolocar o usb para verificar se a reconexão automática está funcionando
- [ ] Acessar tela de calibração e realizar calibração do dispositivo
- [ ] Acessar tela de dispositivos e testar o acionamento de cada dispositivo
- [ ] Acessar tela de ajustes, selecionar jogo Assetto Corsa e verificar se os parâmetros são carregados corretamente
- [ ] Acessar a tela de monitoramento para verificar se o monitoramento do dispositivo está correto durante o jogo
- [ ] Validar funcionamento do shaker no Iracing
- [ ] Validar funcionamento do shaker no Assetto Corsa
- [ ] Validar funcionamento do shaker no Assetto Corsa Competizione
- [ ] Validar funcionamento do shaker no Automobilista 2

### Freio de mão (pedal sport)

- [ ] Validar conexão do dispositivo na tela de monitoramento
- [ ] Remover e recolocar o usb para verificar se a reconexão automática está funcionando
- [ ] Acessar tela de calibração e realizar calibração do dispositivo
- [ ] Acessar tela de ajustes e realizar alterações sutis de parâmetros para verificar se algum erro ocorre
- [ ] Acessar a aba monitor e verificar se o monitoramento do dispositivo está funcionando corretamente durante os jogos

### Cambio de Marcha

- [ ] Validar conexão do dispositivo na tela de monitoramento
- [ ] Remover e recolocar o usb para verificar se a reconexão automática está funcionando
- [ ] Posicionar a alavanca nas posições 1, 2, 3, 4, 5, 6, 7 e R e verificar se a tela de monitoramento registra todas as posições

### Cinto

- [ ] Atualizar firmware do cinto caso uma nova versão esteja disponível
- [ ] Validar conexão do dispositivo na tela de monitoramento
- [ ] Remover e recolocar o usb para verificar se a reconexão automática está funcionando
- [ ] Acessar tela de ajustes e realizar alterações sutis de parâmetros para verificar se algum erro ocorre
- [ ] Acessar a tela de testes e realizar movimentos manuais nos motores para verificar seu funcionamento
- [ ] Na tela de testes ligar e desligar os leds para verificar seu funcionamento
- [ ] Acessar a aba monitor e verificar se o monitoramento do dispositivo está funcionando corretamente durante os jogos
- [ ] Validar funcionamento do cinto e leds no Iracing
- [ ] Validar funcionamento do cinto e leds no Assetto Corsa
- [ ] Validar funcionamento do cinto e leds no Assetto Corsa Competizione
- [ ] Validar funcionamento do cinto e leds no Automobilista 2
