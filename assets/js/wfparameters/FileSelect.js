import React from 'react'
import { csrfToken } from '../utils'
import { Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'

export default class FileSelect extends React.Component {
    constructor(props) {
      super(props);
      var savedFileMeta = this.props.getState();
      if (savedFileMeta !== '') {
        savedFileMeta = JSON.parse(savedFileMeta);
      } else {
        savedFileMeta = false;
      }
      this.state = {
        files: [],
        file: savedFileMeta,
        modalOpen: false
      }
      this.toggleModal = this.toggleModal.bind(this);
    }

    getFiles() {
      var url = '/api/parameters/'+this.props.ps.id+'/event';
      var data = {
        type: 'fetchFiles'
      }
      fetch(url, {
        method: 'post',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
      })
      .then(result => result.json())
      .then(result => {
        this.setState({files: result.files});
      });
    }

    componentDidMount() {
      this.getFiles();
    }

    componentWillReceiveProps() {
      this.getFiles();
    }

    handleClick(file) {
      var url = '/api/parameters/'+this.props.ps.id+'/event';
      var data = {
        file: file,
        type: 'fetchFile'
      }
      fetch(url, {
        method: 'post',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
      })
      .then(() => {
          this.props.saveState(JSON.stringify(file));
          this.setState({file: data.file});
          this.toggleModal();
        }
      );
    }

    toggleModal() {
      this.setState({ modalOpen: !this.state.modalOpen });
    }

    render() {
      var fileList = false;
      var filesModal = false;
      var fileInfo = false;

      if (typeof this.state.files !== 'undefined' && this.state.files.length > 0) {

        fileList = (this.state.files.map( (file, idx) => {
          return (
            <div className="line-item-data" key={idx} onClick={() => this.handleClick(file)}>
              <span className="content-3">{file.name}</span>
            </div>
          );
        }));

        filesModal = (
          <div>
            <div className="button-blue action-button mt-0" onClick={this.toggleModal}>{this.state.file ? 'Change' : 'Choose'} file</div>
            <Modal isOpen={this.state.modalOpen} toggle={this.toggleModal}>
              <ModalHeader toggle={this.toggleModal}>
                <div className='title-4 t-d-gray'>Choose File</div>
              </ModalHeader>
              <ModalBody className="dialog-body">
                <div className="scrolling-list">
                  {fileList}
                </div>
              </ModalBody>
            </Modal>
          </div>
        );
      }

      if (this.state.file) {
        fileInfo = (
          <div>
            <div className={"label-margin t-d-gray content-3"}>File name:</div>
            <div><span className={"t-d-gray content-3 mb-3"}>{this.state.file.name}</span></div>
          </div>
        )
      } else if (fileList) {
        fileInfo = (
          <p>{this.state.files.length} files found.</p>
        )
      }

      if (fileInfo) {
        return (
          <div className="parameter-margin">
            <div className={"parameter-margin version-box"}>
              <div className={"version-item"}>
                {fileInfo}
              </div>
              {filesModal}
            </div>
          </div>
        );
      } else {
        return false;
      }

    }
}
