import React from 'react'
import TweetBox from './TweetBox';


export default function TopTweets({tweetsList}) {
  return (
    <div className="flex flex-col border border-[#D4D4D4] rounded-md mt-5 md:mt-15 text-left p-4 gap-y-2 h-[25rem] w-full">
        <div className="border-b-1 border-[#D4D4D4]">
            <h3 className="pb-2">Tweets</h3>
        </div>
        
        
        {tweetsList ? (
          <div className="flex flex-col pt-4 gap-y-3 overflow-y-scroll scrollbar">
            {tweetsList.map((tweet, index) => (
              <TweetBox key={tweet.id || index} tweetObj={tweet} />
            ))}
          </div>
        ) : (
          <div className="flex flex-wrap justify-center items-center leading-80">No data</div>
        )}
            
       
    </div>
  );
}
