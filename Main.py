
from ast import Return
import os
import sys
import requests
import time
import traceback

from pytube import YouTube
from janela import Ui_MainWindow

from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObject, QThread, pyqtSignal



class ProcuradorDeVideos(QObject):
    '''
    Classe manipulada por um thread.
    Esta classe é responsável por fazer a procura dos videos no youtube, e colocar
    na tela a thumbnail, titulo e duração do vídeo
    '''

    ### OBJETO QUE EMITIRÁ O SINAL PARA O THREAD DE QUANDO FINALIZAR ESTÁ EXECUÇÃO ###
    finished = pyqtSignal()
    def achar_video(self):
        try:

            ### BAIXANDO A THUMB DO VIDEO PARA COLOCAR NA LABEL ###
            yt = YouTube(self.utube.CampoLink.text())
            response = requests.get(yt.thumbnail_url)
            nome = "video_thumb.jpg"

            ### GRAVANDO THUMNAIL BAIXADA ###
            with open("video_thumb.jpg", "wb") as thumbnail:
                thumbnail.write(response.content)
            ##INDICANDO NOME DO AQRUIVO DA IMAGEM QUE SERÁ COLOCADA NA LABEL#
            pix = QPixmap(nome)
            self.utube.PlacetoThumb.setPixmap(pix)

            ### MUDANDO O INDICE DO STACKED WIDGET ###
            self.utube.stackedWidget.setCurrentIndex(0)

            ### COLOCANDO TITULO DO VIDEO NA TELA ###
            self.utube.TituloVideo.setText(str(yt.title))

            ### COLOCANDO DURAÇÃO DO VIDEO NA TELA ###
            self.utube.duracao.setText(f"Duração: {str(time.strftime('%H:%M:%S', time.gmtime(int(yt.length))))}")
        except Exception as e:
            print(traceback.format_exc())

        ### EMITINDO AO THREAD UM SINAL DE QUE A EXECUÇÃO FOI FINZALIZADA ###
        self.finished.emit()


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_program_ui()
        self.show()

    def setup_program_ui(self):
        '''
        Função responsável pelo setup do programa,
        Indicando as funções ativadas quando um botão for clicado. Também
        é responsável por colocar alguns textos em algumas labels do programa
        '''
        self.ui.TituloVideo.setText("")
        self.ui.ProcurandoVideo.setText("Desenvolvido com  ♥  por Winston de Moura")
        self.ui.ProcurandoVideo.setStyleSheet("font-size: 16px;color:white")
        self.ui.Buscar.clicked.connect(lambda: self.procura_videos())
        self.ui.Destino.clicked.connect(lambda: self.select_directory())
        self.ui.Download_MP3.clicked.connect(lambda: self.download("Download MP3"))
        self.ui.Download_HD.clicked.connect(lambda: self.download("Download HD"))
        self.ui.Download_360p.clicked.connect(lambda: self.download("Download 360p"))

    def download(self, tipo_download):
        ### CHECANDO SE O VIDEO EXISTE
        try:
            yt = YouTube(str(self.ui.CampoLink.text()))
        except:
            QtWidgets.QMessageBox.about(self,
             'Erro', 'Url de video inválida.')
            return


        ### CHECANDO SE O DIRETÓRIO SELECIONADO ###
        path_download = self.ui.caminho.text()

        if path_download == "":
            QtWidgets.QMessageBox.about(self,
             'Erro', 'Antes de fazer Download, selecione uma pasta destino acima.')
            return

        if not os.path.exists(path_download):
            QtWidgets.QMessageBox.about(self,
             'Erro', 'Caminho especificado para download não existe.')
            return



        ## MUDANDO LABEL PARA INDICAR QUE O VIDEO ESTÁ SENDO BAIXADO ##
        ##self.ui.TituloVideo.setText("Baixando video...")
        QtWidgets.QMessageBox.about(self,
            'Baixando Vídeo', f'Video sendo baixado. Aguarde!')
        

        ## CHAMANDO FUNÇÃO DE DOWNLOADO PARA CADA TIPO - MP3/MP4 HD/MP4 BAIXA QUALIDADE ##
        if tipo_download == "Download MP3":
            self.Download_mp3(yt, path_download)
        if tipo_download == "Download HD":
            self.Download_mp4(yt, path_download, "MAX")
        if tipo_download == "Download 360p":
            self.Download_mp4(yt, path_download, "MIN")

         ## MUDANDO LABEL PARA INDICAR QUE O VIDEO ESTÁ SENDO BAIXADO ##
        self.ui.TituloVideo.setText("Baixando video...")

        ## APÓS O DOWNLOAD, VOLTAREMOS A LABEL PARA O TITULO DO VÍDEO ##
        self.ui.TituloVideo.setText(str(yt.title))


    def Download_mp4(self, obj_youtube, path_download, qualidade):
        if qualidade == "MAX":
            ### BAIXANDO MP4 NA MENOR RESOLUÇÃO DISPONÍVEL ###
            minha_var = obj_youtube.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first() 
        if qualidade == "MIN":
            ### BAIXANDO MP4 NA MAIOR RESOLUÇÃO DISPONÍVEL ###
            minha_var = obj_youtube.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first() 

        ### MUDANDO NOME DO ARQUIVO DE SAIDA ###
        minha_var.download(filename=f"{obj_youtube.title}_{minha_var.resolution}.mp4".replace("|", ""), output_path=path_download)

        ### VIDEO BAIXADO COM SUCESSO ###
        QtWidgets.QMessageBox.about(self,
             'Sucesso', f'Video baixado com sucesso no diretório: "{path_download}"')
        return


    def Download_mp3(self, obj_youtube, path_download):
        ### BAIXANDO AUDIO MP3 ###
        video = obj_youtube.streams.filter(only_audio=True).first()
        out_file = video.download(output_path=path_download)
  
        ### SALVANDO O ARQUIVO E RENOMEANDO ELE A COM EXTENSÃO MP3 ###
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        
        ### AUDIO BAIXADO COM SUCESSO ###
        QtWidgets.QMessageBox.about(self,
             'Sucesso', f'Video baixado com sucesso no diretório: "{path_download}"')
        return
        

    def select_directory(self):
        ### DEFININDO CAMINHO ONDE O ARQUIVO SERÁ SALVO ###
        diretorio = QtWidgets.QFileDialog.getExistingDirectory(self,
        'Selecione a pasta onde será salvo o PDF:', 'C:\\', QtWidgets.QFileDialog.ShowDirsOnly)
        
        ### FAZENDO VERIFICAÇÕES BÁSICAS ###
        if not diretorio:
            return
        if diretorio.upper() == "C:/":
            QtWidgets.QMessageBox.about(self,
             'Erro', 'Não é permitido salvar arquivos do diretório "C:/", por favor escolha outro diretório.')
            return
        
        ### COLOCANDO NOME DO DIRETÓRIO SELECIONADA NA LABEL ###
        self.ui.caminho.setText(diretorio)
        

    def procura_videos(self):
        '''A importância de criar um novo thread se deve ao fato de que quando
           O programa consulta a api do youtube, a execução principal do PyQt5 
           fica congelada. O thread soluciona esse problema
        '''

        ### INICIANDO UM THREAD PARA FAZER A CONSULTA A API DO YOUTUBE ###
        self.thread = QThread()

        ### INSTANCIANDO UM OBJETO DA CLASSE QUE O THREAD MANIPULARÁ ###
        self.procurador = ProcuradorDeVideos()

        ### INDICANDO AO THREAD O OBJETO QUE SERA USADO ###
        self.procurador.moveToThread(self.thread)

        ### PASSANDO REFERÊNCIA DA MINHA TELA PARA A CLASSE QUE MANIPULA O THREAD ###
        self.procurador.utube = self.ui

        ### INDICANDO O QUE O THREAD DEVE FAZER QUANDO INICIAR ###
        self.thread.started.connect(self.procurador.achar_video)

        ### OBJETO SAIRÁ DO THREAD E SERÁ DELETADO QUANDO SUA EXECUÇÃO ACABAR ###
        self.procurador.finished.connect(self.thread.quit)
        self.procurador.finished.connect(self.procurador.deleteLater)

        ### QUANDO O THREAD FINALIZAR ELE SERÁ AUTODESTRUIDO ###
        self.thread.finished.connect(self.thread.deleteLater)
        
        ### INICIANDO PROCESSO ###
        self.thread.start()

        ### DESABILITANDO BOTÃO DE "BUSCAR" NA TELA ENQUANTO O THREAD ESTÁ ATIVO ###
        self.ui.Buscar.setEnabled(False)

        ### HABILITANDO O BOTÃO DE "BUSCAR" NA TELA QUANDO O THREAD É FINALIZADO ###
        self.thread.finished.connect(
             lambda: self.ui.Buscar.setEnabled(True)
         )


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())

