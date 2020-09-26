/*  TRABALHO DE REDES INDUSTRIAIS 
 *
 *   Autor: Bruno Gabriel Flores Sampaio
 *   Data : 26/06/2020
 *
 *   Descriço: 
       Usando um Arduino NANO, farei o  sensoriamento
       de objetos dentro de uma area limitada em 180º
       fazendo o uso de um  HC-SR04, um sensor ultra-
       Sonico. 
       O Arduino  estara conectado ao Serial  e um script
       em python fara a leitura dos dados da porta e uti-
       lizando  transmissoes via sockets UDP, fara o con-
       trole remoto ou local do sistema.
 *
 *   Primeira atualizaçao.  
 *
 */

#include <Servo.h>

#define CM 28 // Constante divisor de Centimetros
#define IN 72 // Constante divisor de Polegadas 

// DEFINIÇAO DE PROCESSO
#define MANUAL   '1'
#define AUTO     '2'
#define REMOTO   '3'

// TAMANHO DO BUFFER EM BYTES 
#define BUFFER_LEN 32

// PINOS USADOS NO ARDUINO
const int TRIG  = 4;
const int ECHO  = 5;
const int POT   = A0;
const int BOT   = 2;
const int SERVO = 11;

// VARIVEIS DE CONTROLE
static byte *serialReadArray;
static byte *lineReadSerial;

byte processDefinition = AUTO;

long int tempoCompensado  = 0;
long int tempoCorrido     = 0;

long int processKeepAlive = 1000;
long int processAlive     = 0;


// VARIVEIS DE INTERESSE 
float distancia = 0;
float angulo    = 0;

// DEFINIÇAO DO SERVO
Servo servito;

String inputString = "";
boolean stringComplete = false;

// INICIO DO CODIGO
void setup() {

  // PARA O SENSOR ULTRASSONICO
  digitalWrite(3, HIGH);
  digitalWrite(6, LOW);

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  // PARA O POTENCIOMETRO
  pinMode(POT, INPUT);

  // ATTACH DO BOTÃO
  pinMode(BOT, INPUT_PULLUP);
  //attachInterrupt(0, botEmergencia, RISING);

  // PARA O SERVO
  servito.attach(SERVO);

  // PARA INICIAR O SERIAL 
  Serial.begin(9600);
  
  // SERPARA n BYTES PARA O INPUT
  inputString.reserve(BUFFER_LEN);

}

bool flagRemoto = false;
bool flagNewCap = false;

void loop(){

  tempoCorrido = millis();

  // POR QUESTÕES  DE SEGURANÇA,  O PROCESSO  REMOTO SÓ  PODE
  // SER CHAMADO CASO A DEFINIÇÃO DO PROCESSO NÃO SEJA MANUAL
  if (processDefinition != MANUAL){

    if (stringComplete) {
      
      union{
        byte bytes[2] = {inputString[4],inputString[3]};
        int num_int;
      } n;
      
      processDefinition = (int)inputString[0]; 

      if (inputString[0] == REMOTO){
        angulo     = n.num_int;
        flagNewCap = true;
      }
      inputString = "";
      stringComplete = false;
    
    }
  }

  if (processDefinition == REMOTO){
    // INICIA A CONTAGEM DO TEMPO 
    if (flagRemoto == false || flagNewCap == true){
      flagRemoto         = true;
      flagNewCap         = false;
      processAlive       = millis();
    }

    // CONFERE O TEMPO DA COMUNICAÇÃO INATIVA
    if(processKeepAlive < (millis()-processAlive)){
      processDefinition = AUTO;
      processAlive      = 0;
      flagRemoto        = false;
    }

  }else if (processDefinition == MANUAL){                 
    // MODO MANUAL - POTENCIOMETRO GIRANDO MANUALMENTE
    angulo = map(analogRead(POT), 0, 1023, 0, 180);
  
  }else if (processDefinition == AUTO){
    // MODO AUTOMTICO - LAÇO DE REPETIÇAO FOR
    angulo > 180 ? angulo = 0 : angulo++;
  }

  servito.write((int)angulo);

  Serial.print((int)angulo);
  Serial.print(',');
  
  //float dist = lerDistancia(100);
  float dist = random(100,150);
  byte distBytes[4];

  union {
    float float_variable;
    byte temp_array[4];
  }u;
  
  u.float_variable = dist;
  memcpy(&distBytes[0], u.temp_array, 4);

  for (int i=0; i<4; i++){
    Serial.print(" ");
    Serial.print(distBytes[i],DEC);
  }
  Serial.println();

  // PARA O PROCESSO LEVAR APENAS 1 SEGUNDO FAZEMOS A COMPENSAÇAO 
  tempoCompensado = millis() - tempoCorrido;
  delay(100 - tempoCompensado);
}


// BOTAO DE EMERGENCIA - COLOCA NO MODO MANUAL
void botEmergencia(){
  processAlive = 0;
  (processDefinition == MANUAL) ? processDefinition = AUTO : processDefinition = MANUAL;
}


float lerDistancia(long int overtime){

  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  long int duracao = pulseIn(ECHO, HIGH, overtime*1000);
  return ( duracao / (CM * 2.0));
}


void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read(); 
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    } 
  }
}


