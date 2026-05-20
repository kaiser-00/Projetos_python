# Engine de Otimulação Física - Núcleo Computacional (C++)

Este repositório contém o motor de processamento físico desenvolvido nativamente em C++ para fundamentação de artigo e publicação científica em andamento na **EEB Prefeito Amádio Dalago**, sob orientação da professora **Crisley**.

## 🎯 Objetivo do Projeto
O objetivo deste módulo é isolar e computar equações complexas da Cinemática (Movimento Retilíneo Uniforme - MRU e Movimento Retilíneo Uniforme Variado - MRUV) utilizando estruturas de dados otimizadas (`structs`), garantindo alta performance e baixo consumo de memória. 

Esses scripts foram arquitetados para funcionar como uma biblioteca própria, cujos módulos matemáticos serão integrados ao ecossistema Python via *bindings* de linguagem.

## ♿ Foco em Acessibilidade Cognitiva e Inclusão (TEA)
O motor físico alimentará uma interface gráfica multiplataforma desenvolvida em **PySide6 (Qt6)**. O grande diferencial inovador do projeto é a implementação de recursos de acessibilidade nativa (`QAccessible`), contando com uma interface simplificada e paleta de cores adaptada para mitigar sobrecargas sensoriais em estudantes dentro do **Espectro Autista (TEA)**.

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** C++ Moderno
- **Estruturação:** Funções puras encapsuladas em `structs` para acoplamento flexível.
- **Ambiente de Testes:** Compilação nativa via GCC/G++ executada em ambiente Windows PowerShell.