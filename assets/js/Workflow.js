// This is the main script for the Workflow view

import React from 'react'
import WorkflowNavBar from './WorkflowNavBar'
import OutputPane from './OutputPane'
import Lesson from './lessons/Lesson'
import PropTypes from 'prop-types'
import ModuleStack from './ModuleStack'
import { logUserEvent } from './utils'
import { connect } from 'react-redux'

export function MaybeNotYourWorkflow(props) {
  if (!props.isReadOnly && !props.isAnonymous) {
    return null // it's your workflow
  }

  const F = React.Fragment

  let suggestion = null
  if (props.isLoggedIn) {
    suggestion = <p className="suggestion">Duplicate it to save your changes</p>
  } else {
    suggestion = <p className="suggestion"><a href={`/account/login/?next=/workflows/${props.workflowId}`}>Sign in</a> to save your changes</p>
  }

  let inner, className
  if (props.isAnonymous) {
    className = 'is-anonymous'
    inner = (
      <F>
        <h3>This is a Demo workflow -</h3>
        <p className="message"></p>
        {suggestion}
      </F>
    )
  } else if (props.isReadOnly) {
    className = 'is-read-only'
    inner = (
      <F>
        <h3>You are viewing a shared workflow -</h3>
        <p className="message"></p>
        {suggestion}
      </F>
    )
  }

  return (
    <div className={`not-your-workflow ${className}`}>{inner}</div>
  )
}

// ---- WorkflowMain ----

export class Workflow extends React.Component {
  static propTypes = {
    api:                PropTypes.object.isRequired,
    isReadOnly:         PropTypes.bool.isRequired,
    isAnonymous:        PropTypes.bool.isRequired,
    workflow:           PropTypes.object.isRequired,
    selected_wf_module: PropTypes.number,             // null means no selected module
    loggedInUser:       PropTypes.object,             // undefined if no one logged in (viewing public wf)
  }

  constructor(props) {
    super(props);

    this.state = {
        isFocusModuleStack: false,
        overlapping: false, // Does the right pane overlap the left pane? Used to set focus, draw shadows, etc
    };
  }

  setOverlapping = (overlapping) => {
    this.setState({
      overlapping
    });
  }

  setFocusModuleStack = () => {
    this.setState({
      isFocusModuleStack: true,
    });
  }

  setFocusOutputPane = () => {
    this.setState({
      isFocusModuleStack: false,
    });
  }

  render() {
    const selectedWfModule = this.props.workflow.wf_modules[this.props.selected_wf_module];

    let className = 'workflow-root'
    if (this.props.lesson) {
      className += ' in-lesson'
    }

    return (
        <div className={className}>
          { this.props.lesson ? <Lesson {...this.props.lesson} logUserEvent={logUserEvent} /> : '' }

          <div className="workflow-container">
            <WorkflowNavBar
              workflow={this.props.workflow}
              api={this.props.api}
              isReadOnly={this.props.workflow.read_only}
              loggedInUser={this.props.loggedInUser}
            />

            <div className={"workflow-columns" + (this.state.overlapping ? " overlapping" : "")}>
              <ModuleStack
                api={this.props.api}
                focus={this.state.isFocusModuleStack}
                setFocus={this.setFocusModuleStack}
              />
              <OutputPane
                selectedWfModuleId={selectedWfModule ? selectedWfModule.id : null}
                revision={this.props.workflow.revision}
                api={this.props.api}
                htmlOutput={selectedWfModule ? selectedWfModule.html_output : null}
                workflow={this.props.workflow}
                focus={!this.state.isFocusModuleStack}
                setFocus={this.setFocusOutputPane}
                setOverlapping={this.setOverlapping}
              />
            </div>

            <MaybeNotYourWorkflow
              workflowId={this.props.workflow.url_id}
              isLoggedIn={!!this.props.loggedInUser}
              isReadOnly={this.props.isReadOnly}
              isAnonymous={this.props.isAnonymous}
              />
          </div>
          <div className='help-container'>
            <a target="_blank" href="http://help.workbenchdata.com/getting-started/build-your-first-workflow" >
              <div className='help-shortcut btn'>
                <div className='icon-knowledge' />
              </div>
            </a>
          </div>

        </div>
    );
  }
}

// Handles addModule (and any other actions that change top level workflow state)
const mapStateToProps = (state) => {
  return {
    workflow: state.workflow,
    selected_wf_module: state.selected_wf_module,
    loggedInUser: state.loggedInUser,
    isAnonymous: state.workflow.is_anonymous,
    isReadOnly: state.workflow.read_only,
  }
};


export default connect(
  mapStateToProps
)(Workflow);
